#gesture_controller.py
try:
    import cv2
    import mediapipe as mp
    from score_state import update_score, reset_gesture_flag
    OPENCV_AVAILABLE = True
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
except ImportError:
    OPENCV_AVAILABLE = False
    mp_hands = None
    mp_drawing = None
    def update_score(*args):
        pass
    def reset_gesture_flag():
        pass

def count_fingers(hand_landmarks):
    """Count fingers but exclude special gesture combinations"""
    # Get landmark positions for special gesture detection
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    
    # Check if this is a pinch gesture (should be handled as Dot Ball)
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_index_distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
    
    pinch_gesture = (thumb_index_distance < 0.05 and          # Thumb and index very close
                     middle_tip.y > middle_pip.y and          # Middle finger down
                     ring_tip.y > ring_pip.y and              # Ring finger down
                     pinky_tip.y > pinky_pip.y)               # Pinky down
    
    # Check if this is a thumb out gesture (should be handled as Wide)
    thumb_out = (thumb_tip.y < thumb_ip.y and           # Thumb up/out
                 index_tip.y > index_pip.y and          # Index finger down
                 middle_tip.y > middle_pip.y and        # Middle finger down
                 ring_tip.y > ring_pip.y and            # Ring finger down
                 pinky_tip.y > pinky_pip.y)             # Pinky down
    
    if pinch_gesture or thumb_out:
        return None  # Don't count fingers for special gestures
    
    # Regular finger counting
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
    """Detect special gestures for cricket extras"""
    # Get landmark positions
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    
    # Pinch gesture (thumb + index almost touching) for Dot Ball
    thumb_index_distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
    pinch_gesture = (thumb_index_distance < 0.05 and          # Thumb and index very close
                     middle_tip.y > middle_pip.y and          # Middle finger down
                     ring_tip.y > ring_pip.y and              # Ring finger down
                     pinky_tip.y > pinky_pip.y)               # Pinky down
    
    # Thumbs up gesture (for No Ball) - vertical thumb
    thumb_up = (thumb_tip.y < thumb_ip.y and 
                index_tip.y > index_pip.y and 
                middle_tip.y > middle_pip.y and
                ring_tip.y > ring_pip.y and
                pinky_tip.y > pinky_pip.y and
                # Additional check to distinguish from wide gesture
                abs(thumb_tip.x - thumb_ip.x) < 0.05)  # Thumb more vertical for no-ball
    
    # Fist with thumb out (like thumbs up but horizontal) for Wide
    thumb_out = (thumb_tip.y < thumb_ip.y and           # Thumb up/out
                 index_tip.y > index_pip.y and          # Index finger down
                 middle_tip.y > middle_pip.y and        # Middle finger down
                 ring_tip.y > ring_pip.y and            # Ring finger down
                 pinky_tip.y > pinky_pip.y)             # Pinky down
    
    # Pointing gesture (for Bye) - only index finger up
    pointing = (thumb_tip.y > thumb_ip.y and
                index_tip.y < index_pip.y and 
                middle_tip.y > middle_pip.y and
                ring_tip.y > ring_pip.y and
                pinky_tip.y > pinky_pip.y and
                # Additional check: ensure other fingers are significantly down
                (middle_pip.y - middle_tip.y) > 0.02 and
                (ring_pip.y - ring_tip.y) > 0.02 and
                (pinky_pip.y - pinky_tip.y) > 0.02)
    
    if pinch_gesture:
        return "dot_ball"
    elif thumb_up:
        return "no_ball"
    elif thumb_out:
        return "wide"
    elif pointing:
        return "bye"
    else:
        return None

def run_gesture_controller():
    if not OPENCV_AVAILABLE or mp_hands is None:
        print("OpenCV/MediaPipe not available - gesture detection disabled")
        return
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.5,
                        max_num_hands=1) as hands:
        last_fingers = None
        last_special = None
        
        # Gesture confirmation variables
        current_gesture = None
        gesture_start_time = None
        confirmation_delay = 5.0  # 5 seconds confirmation time
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            image = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1)
            results = hands.process(image)
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            detected_gesture = None
            gesture_text = ""
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Check for special gestures first
                    special_gesture = detect_special_gestures(hand_landmarks)
                    
                    if special_gesture:
                        detected_gesture = f"special_{special_gesture}"
                        gesture_text = f"Special: {special_gesture.upper()}"
                        if special_gesture == "dot_ball":
                            gesture_text += "(Dot Ball)"
                        elif special_gesture == "no_ball":
                            gesture_text += " (No Ball + Free Hit)"
                        elif special_gesture == "wide":
                            gesture_text += " 👍 (Wide)"
                        elif special_gesture == "bye":
                            gesture_text += " (Bye)"
                    else:
                        # Handle regular finger counting
                        fingers_count = count_fingers(hand_landmarks)
                        
                        if fingers_count is not None:
                            detected_gesture = f"fingers_{fingers_count}"
                            gesture_text = f"Fingers: {fingers_count}"
                            if fingers_count == 0:
                                gesture_text += " 🏏 OUT!"
                            elif fingers_count == 1:
                                gesture_text += " (1 Run)"
                            elif fingers_count == 2:
                                gesture_text += " ✌️ (2 Runs)"
                            elif fingers_count == 3:
                                gesture_text += " (3 Runs)"
                            elif fingers_count == 4:
                                gesture_text += " (4 Runs)"
                            elif fingers_count == 5:
                                gesture_text += " 🖐️ (6 Runs)"
                    
                    # Gesture confirmation logic
                    import time
                    current_time = time.time()
                    
                    if detected_gesture:
                        if current_gesture != detected_gesture:
                            # New gesture detected
                            current_gesture = detected_gesture
                            gesture_start_time = current_time
                        else:
                            # Same gesture held
                            time_held = current_time - gesture_start_time
                            remaining_time = confirmation_delay - time_held
                            
                            if remaining_time > 0:
                                # Show countdown
                                gesture_text += f" - Hold for {remaining_time:.1f}s more"
                                # Show progress bar
                                progress = int((time_held / confirmation_delay) * 50)
                                progress_bar = "█" * progress + "░" * (50 - progress)
                                cv2.putText(image_bgr, f"Confirming: [{progress_bar}]", (10, 70), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                            else:
                                # Gesture confirmed!
                                gesture_text += " ✅ CONFIRMED!"
                                
                                # Execute the gesture action
                                if detected_gesture.startswith("special_"):
                                    special_action = detected_gesture.replace("special_", "")
                                    if special_action != last_special:
                                        update_score(special_action)
                                        last_special = special_action
                                        last_fingers = None
                                elif detected_gesture.startswith("fingers_"):
                                    finger_count = int(detected_gesture.replace("fingers_", ""))
                                    if finger_count != last_fingers:
                                        update_score(finger_count)
                                        last_fingers = finger_count
                                        last_special = None
                                
                                # Reset after confirmation
                                current_gesture = None
                                gesture_start_time = None
                    
                    cv2.putText(image_bgr, gesture_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if "CONFIRMED" in gesture_text else (255, 255, 0), 2)
                    break
            else:
                # No hand detected - reset everything
                current_gesture = None
                gesture_start_time = None
                last_fingers = None
                last_special = None
                reset_gesture_flag()
                cv2.putText(image_bgr, "Show hand gesture...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
                    
            
            # Show gesture instructions
            instructions = [
                "HOLD gesture for 5 seconds to confirm",
                "0 fingers: OUT | 1,2,3,4 fingers: runs",
                "🖐️ Five fingers (open palm): 6 Runs (Six)",
                "🤏 Pinch (thumb+index close): Dot Ball",
                "👍 Thumbs Up (vertical): No Ball",
                "👍 Thumb Out (horizontal): Wide", 
                "👉 Point: Bye"
            ]
            
            for i, instruction in enumerate(instructions):
                cv2.putText(image_bgr, instruction, (10, image_bgr.shape[0] - 100 + i*15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            cv2.imshow('Cricket Gesture Controller - Press Q to Quit', image_bgr)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()