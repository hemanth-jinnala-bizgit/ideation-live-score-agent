# =====================================================
# FILE 3: main_app.py (Main Streamlit application)
# =====================================================

import streamlit as st
from score_state import get_score, reset_match, undo_last_ball, get_match_status, set_match_overs
import threading
from gesture_controller import run_gesture_controller
import time

st.set_page_config(
    page_title="Cricket Scoreboard - Gesture Control", 
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 Live Gesture-Controlled Cricket Scoreboard")

# Match Setup Section
if 'match_started' not in st.session_state:
    st.session_state.match_started = False

if not st.session_state.match_started:
    st.markdown("### 🏏 Match Setup")
    
    teams = [
        "Chennai Super Kings (CSK)",
        "Royal Challengers Bengaluru (RCB)", 
        "Rajasthan Royals (RR)",
        "Punjab Kings (PBKS)",
        "Kolkata Knight Riders (KKR)",
        "Mumbai Indians (MI)",
        "Gujarat Titans (GT)",
        "Delhi Capitals (DC)",
        "Sunrisers Hyderabad (SRH)",
        "Lucknow Super Giants (LSG)"
    ]
    
    setup_col1, setup_col2, setup_col3 = st.columns(3)
    
    with setup_col1:
        team1 = st.selectbox("Select Team 1", teams, key="team1")
    
    with setup_col2:
        available_teams = [t for t in teams if t != team1]
        team2 = st.selectbox("Select Team 2", available_teams, key="team2")
    
    with setup_col3:
        overs = st.selectbox("Match Overs", [1,5, 10, 15, 20], index=3, key="overs")
    
    batting_first = st.radio("Who bats first?", [team1, team2], key="batting_first")
    
    if st.button("🚀 Start Match", type="primary"):
        st.session_state.match_started = True
        st.session_state.match_team1 = team1
        st.session_state.match_team2 = team2
        st.session_state.match_overs = overs
        st.session_state.match_batting_first = batting_first
        st.session_state.match_bowling_first = team2 if batting_first == team1 else team1
        set_match_overs(overs)
        reset_match()
        st.rerun()
    
    st.stop()  # Don't show the rest of the app until match is started

# Match Info Display
st.markdown(f"**{st.session_state.match_batting_first}** vs **{st.session_state.match_bowling_first}** | {st.session_state.match_overs} Overs")
st.markdown(f"**Status:** {get_match_status()}")
if st.button("🔄 New Match Setup"):
    st.session_state.match_started = False
    for key in ['match_team1', 'match_team2', 'match_overs', 'match_batting_first', 'match_bowling_first']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Gesture Instructions
    with st.expander("🤏 Gesture Instructions", expanded=True):
        st.markdown("""
        **Regular Scoring Gestures:**
        - 👊 **Fist (0 fingers)**: Wicket
        - ☝️ **1 finger**: 1 run
        - ✌️ **2 fingers**: 2 runs  
        - 🤟 **3 fingers**: 3 runs
        - 🖖 **4 fingers**: 4 runs (boundary)
        - ✋ **5 fingers (open palm)**: 6 runs (six!)
        - 🤏 **Pinch (thumb + index close)**: Dot Ball (0 runs)
        
        **Special Cricket Signals:**
        - 👍 **Thumbs Up (vertical)**: No Ball (+1 run, Free Hit next)
        - 👍 **Thumb Out (horizontal)**: Wide (+1 run, re-bowl)
        - 👉 **Point Finger**: Bye (+1 run, legal delivery)
        
        **Cricket Rules:**
        - **Free Hit**: After No Ball, batsman can't get out (except run out)
        - **Extras**: No Balls & Wides don't count as legal deliveries
        - **Byes**: Runs scored without bat, count as legal deliveries
        
        **Camera Window:**
        - A separate OpenCV window will open for gesture detection
        - Show your hand gestures to the camera
        - Press 'Q' in the camera window to stop gesture detection
        """)
    
    # Manual controls for additional extras
    st.markdown("### 🎮 Manual Controls")
    
    manual_col1, manual_col2, manual_col3 = st.columns(3)
    
    with manual_col1:
        if st.button("LB", help="Leg Bye"):
            from score_state import update_score
            update_score("leg_bye")
            st.rerun()
    
    with manual_col2:
        if st.button("🔄 Reset Match"):
            reset_match()
            st.rerun()
    
    with manual_col3:
        if st.button("↩️ Undo Last Ball"):
            undo_last_ball()
            st.rerun()
    
    # Camera controls
    camera_col1, camera_col2 = st.columns(2)
    
    with camera_col1:
        if st.button("📹 Start Gesture Detection", type="primary"):
            if 'gesture_started' not in st.session_state:
                threading.Thread(target=run_gesture_controller, daemon=True).start()
                st.session_state['gesture_started'] = True
                st.success("✅ Gesture detection started! Check the camera window.")
            else:
                st.info("Gesture detection is already running!")
    
    with camera_col2:
        st.info("📱 Camera opens in separate window")

with col2:
    pass

# Live score display
st.markdown("---")

# Create placeholder for live updates
score_placeholder = st.empty()

# Continuous score update loop
while True:
    with score_placeholder.container():
        (runs, wickets, overs, balls, last_action, ball_by_ball, cooldown_remaining, 
         extras, wides, noballs, byes, legbyes, free_hit, innings, first_innings_score, 
         match_complete, winner) = get_score()
        
        # Determine current batting team
        if innings == 1:
            current_batting_team = st.session_state.match_batting_first
        else:
            current_batting_team = st.session_state.match_bowling_first
        
        # Main score display
        if match_complete:
            # Match complete display
            if winner == "chasing_team":
                winner_team = st.session_state.match_bowling_first if innings == 2 else st.session_state.match_batting_first
                st.markdown(f"""
                <div style="background-color: #d4edda; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; border: 3px solid #28a745;">
                    <h2 style="color: #155724; margin: 0;">🏆 MATCH COMPLETE!</h2>
                    <h1 style="color: #28a745; margin: 10px 0; font-size: 2.5em;">{winner_team} WINS!</h1>
                    <h3 style="color: #155724; margin: 10px 0;">Final Score: {runs}/{wickets} ({overs}.{balls} overs)</h3>
                    <h4 style="color: #155724; margin: 10px 0;">First Innings: {first_innings_score}</h4>
                    <p style="color: #155724; margin: 10px 0; font-size: 1.1em;"><strong>{last_action}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            elif winner == "defending_team":
                winner_team = st.session_state.match_batting_first if innings == 2 else st.session_state.match_bowling_first
                st.markdown(f"""
                <div style="background-color: #d4edda; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; border: 3px solid #28a745;">
                    <h2 style="color: #155724; margin: 0;">🏆 MATCH COMPLETE!</h2>
                    <h1 style="color: #28a745; margin: 10px 0; font-size: 2.5em;">{winner_team} WINS!</h1>
                    <h3 style="color: #155724; margin: 10px 0;">Final Score: {runs}/{wickets} ({overs}.{balls} overs)</h3>
                    <h4 style="color: #155724; margin: 10px 0;">First Innings: {first_innings_score}</h4>
                    <p style="color: #155724; margin: 10px 0; font-size: 1.1em;"><strong>{last_action}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            else:  # tie
                st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; border: 3px solid #ffc107;">
                    <h2 style="color: #856404; margin: 0;">🤝 MATCH TIED!</h2>
                    <h1 style="color: #856404; margin: 10px 0; font-size: 2.5em;">It's a Tie!</h1>
                    <h3 style="color: #856404; margin: 10px 0;">Final Score: {runs}/{wickets} ({overs}.{balls} overs)</h3>
                    <h4 style="color: #856404; margin: 10px 0;">First Innings: {first_innings_score}</h4>
                    <p style="color: #856404; margin: 10px 0; font-size: 1.1em;"><strong>{last_action}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Regular score display
            target_info = ""
            if innings == 2:
                target = first_innings_score + 1
                need = target - runs
                balls_left = (st.session_state.match_overs * 6) - (overs * 6 + balls)
                target_info = f"<p style='color: #dc3545; margin: 5px 0; font-weight: bold;'>Target: {target} | Need: {need} runs in {balls_left} balls</p>"
            
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;">
                <h3 style="color: #1f77b4; margin: 0;">{current_batting_team} - Innings {innings}</h3>
                <h1 style="color: #1f77b4; margin: 0; font-size: 3em;">{runs}/{wickets}</h1>
                <h2 style="color: #666; margin: 15px 0;">Overs: {overs}.{balls}/{st.session_state.match_overs}</h2>
                {target_info}
                <p style="color: #888; margin: 10px 0; font-size: 1.1em;"><strong>Last Action:</strong> {last_action}</p>
                {f'<p style="color: #ff6b6b; margin: 5px 0; font-weight: bold;">🔥 FREE HIT NEXT BALL!</p>' if free_hit else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Show first innings score if in second innings
            if innings == 2:
                st.markdown(f"""
                <div style="background-color: #e9ecef; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;">
                    <h4 style="color: #495057; margin: 0;">First Innings: {st.session_state.match_batting_first} - {first_innings_score}</h4>
                </div>
                """, unsafe_allow_html=True)
        
        # Extras breakdown
        if extras > 0:
            st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4 style="color: #856404; margin: 0;">📊 Extras Breakdown (Total: {extras})</h4>
                <div style="display: flex; justify-content: space-around; margin-top: 10px;">
                    <span style="color: #856404;"><strong>Wides:</strong> {wides}</span>
                    <span style="color: #856404;"><strong>No Balls:</strong> {noballs}</span>
                    <span style="color: #856404;"><strong>Byes:</strong> {byes}</span>
                    <span style="color: #856404;"><strong>Leg Byes:</strong> {legbyes}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Cooldown indicator
        if cooldown_remaining > 0:
            st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0; border-left: 5px solid #ffc107;">
                <h4 style="color: #856404; margin: 0;">⏳ Gesture Cooldown Active</h4>
                <p style="color: #856404; margin: 5px 0;">Next gesture accepted in: <strong>{cooldown_remaining:.1f} seconds</strong></p>
                <p style="color: #856404; margin: 5px 0; font-size: 0.9em;">Gestures are ignored during this period to prevent accidental scoring</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #d1edff; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0; border-left: 5px solid #0066cc;">
                <h4 style="color: #004085; margin: 0;">✅ Ready for Next Gesture</h4>
                <p style="color: #004085; margin: 5px 0;">Show your hand gesture to the camera to score</p>
                {f'<p style="color: #ff6b6b; margin: 5px 0; font-weight: bold;">🔥 Next ball is a FREE HIT!</p>' if free_hit else ''}
            </div>
            """, unsafe_allow_html=True)
        
        # Ball by ball display
        if ball_by_ball:
            st.markdown("### 📝 Ball by Ball")
            # Show last 18 balls (3 overs)
            recent_balls = ball_by_ball[-18:] if len(ball_by_ball) > 18 else ball_by_ball
            balls_text = " | ".join(recent_balls)
            st.code(balls_text, language=None)
            
            # Show total balls bowled
            st.caption(f"Total deliveries: {len(ball_by_ball)} | Legal balls: {balls + (overs * 6)}")
        
        # Match statistics
        if balls > 0 or overs > 0:
            total_balls = overs * 6 + balls
            if total_balls > 0:
                run_rate = round((runs / total_balls) * 6, 2)
                st.markdown(f"**Current Run Rate:** {run_rate} runs per over")
                
        # Legend for ball symbols
        st.markdown("""
        **Ball Symbols:** 
        • = Dot, W = Wicket, 1-6 = Runs, NB = No Ball, WD = Wide, B1 = Bye, LB1 = Leg Bye
        """)
    
    # Update every second
    time.sleep(1)