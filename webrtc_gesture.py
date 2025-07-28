import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import cv2
import mediapipe as mp
import numpy as np
from score_state import update_score, reset_gesture_flag
import time

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Global variables for gesture detection
last_gesture = None
last_gesture_time = 0
confirmation_delay = 2.0

def count_fingers(hand_landmarks):
    """Count fingers from hand landmarks"""
    fingers = []
    # Thumb
    fingers.append(int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x <
                      hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x))
    # Fingers
    for tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                   mp_hands.HandLandmark.RING_FINGER_TIP,
                   mp_hands.HandLandmark.PINKY_TIP]:
        tip = hand_landmarks.landmark[tip_id]
        dip = hand_landmarks.landmark[tip_id - 2]
        fingers.append(int(tip.y < dip.y))
    return sum(fingers)

def detect_special_gestures(hand_landmarks):
    """Detect special gestures"""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    
    # Pinch gesture for dot ball
    thumb_index_distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
    if thumb_index_distance < 0.05:
        return "dot_ball"
    
    # Thumbs up for no ball
    if (thumb_tip.y < thumb_ip.y and 
        index_tip.y > index_pip.y and 
        middle_tip.y > middle_pip.y):
        return "no_ball"
    
    return None

def process_frame(frame):
    """Process video frame for gesture detection"""
    global last_gesture, last_gesture_time
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.5,
                        max_num_hands=1) as hands:
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Detect gestures
                special_gesture = detect_special_gestures(hand_landmarks)
                current_time = time.time()
                
                if special_gesture:
                    gesture_text = f"Special: {special_gesture.upper()}"
                    detected_gesture = f"special_{special_gesture}"
                else:
                    finger_count = count_fingers(hand_landmarks)
                    if finger_count == 0:
                        gesture_text = "WICKET!"
                    elif finger_count == 5:
                        gesture_text = "6 RUNS (Six!)"
                    else:
                        gesture_text = f"{finger_count} RUN{'S' if finger_count > 1 else ''}"
                    detected_gesture = f"fingers_{finger_count}"
                
                # Gesture confirmation logic
                if detected_gesture == last_gesture:
                    time_held = current_time - last_gesture_time
                    if time_held >= confirmation_delay:
                        # Execute gesture
                        if special_gesture:
                            update_score(special_gesture)
                        else:
                            update_score(finger_count)
                        
                        gesture_text += " ✅ CONFIRMED!"
                        last_gesture = None
                        last_gesture_time = 0
                    else:
                        remaining = confirmation_delay - time_held
                        gesture_text += f" - Hold {remaining:.1f}s"
                else:
                    last_gesture = detected_gesture
                    last_gesture_time = current_time
                
                # Display gesture text
                cv2.putText(frame, gesture_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Show hand gesture...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
            last_gesture = None
            last_gesture_time = 0
            reset_gesture_flag()
    
    return frame

class VideoProcessor:
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        processed_img = process_frame(img)
        return processed_img

def start_webrtc_gesture_detection():
    """Start WebRTC gesture detection"""
    RTC_CONFIGURATION = RTCConfiguration({
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    })
    
    webrtc_ctx = webrtc_streamer(
        key="gesture-detection",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    if webrtc_ctx.video_processor:
        st.success("🎥 Gesture detection active! Show your gestures to the camera.")
        st.info("Hold gesture for 2 seconds to confirm scoring.")
    
    return webrtc_ctx