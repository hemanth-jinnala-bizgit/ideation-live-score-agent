# # score_state.py
# import streamlit as st
# import time

# # Global state dictionary
# state = {
#     "runs": 0,
#     "wickets": 0,
#     "balls": 0,
#     "extras": 0,  # Track extras separately
#     "wides": 0,
#     "noballs": 0,
#     "byes": 0,
#     "legbyes": 0,
#     "last_updated_fingers": None,
#     "last_action": "Match Started",
#     "ball_by_ball": [],
#     "last_gesture_time": 0,
#     "cooldown_period": 5.0,  # 5 seconds cooldown
#     "free_hit": False  # Track if next ball is a free hit
# }

# def get_score():
#     """Get current match score"""
#     overs = state["balls"] // 6
#     balls = state["balls"] % 6
    
#     # Calculate remaining cooldown time
#     current_time = time.time()
#     time_since_last = current_time - state["last_gesture_time"]
#     cooldown_remaining = max(0, state["cooldown_period"] - time_since_last)
    
#     return (state["runs"], state["wickets"], overs, balls, state["last_action"], 
#             state["ball_by_ball"], cooldown_remaining, state["extras"], state["wides"], 
#             state["noballs"], state["byes"], state["legbyes"], state["free_hit"])

# def update_score(gesture):
#     """Update score based on gesture with 5-second cooldown"""
#     current_time = time.time()
    
#     # Check if we're still in cooldown period
#     if current_time - state["last_gesture_time"] < state["cooldown_period"]:
#         return  # Ignore gesture during cooldown
    
#     # Check for duplicate gesture
#     if state["last_updated_fingers"] == gesture:
#         return  # prevent duplicate score
    
#     # Update the last gesture time
#     state["last_gesture_time"] = current_time
    
#     # Handle special gestures first
#     if gesture == "no_ball":
#         state["runs"] += 1  # No ball gives 1 run penalty
#         state["extras"] += 1
#         state["noballs"] += 1
#         state["free_hit"] = True  # Next ball is a free hit
#         state["last_action"] = "NO BALL! (+1 run, Free Hit next)"
#         state["ball_by_ball"].append("NB")
#         # No ball doesn't count as a legal delivery, so don't increment balls
        
#     elif gesture == "wide":
#         state["runs"] += 1  # Wide gives 1 run penalty
#         state["extras"] += 1
#         state["wides"] += 1
#         state["last_action"] = "WIDE! (+1 run)"
#         state["ball_by_ball"].append("WD")
#         # Wide doesn't count as a legal delivery, so don't increment balls
        
#     elif gesture == "bye":
#         # Byes don't add to batsman's score but add to team total
#         # For simplicity, we'll add 1 bye run (can be extended for multiple byes)
#         state["runs"] += 1
#         state["extras"] += 1
#         state["byes"] += 1
#         state["balls"] += 1
#         state["last_action"] = "BYE! (+1 run)"
#         state["ball_by_ball"].append("B1")
        
#     elif gesture == "leg_bye":
#         # Leg byes don't add to batsman's score but add to team total
#         state["runs"] += 1
#         state["extras"] += 1
#         state["legbyes"] += 1
#         state["balls"] += 1
#         state["last_action"] = "LEG BYE! (+1 run)"
#         state["ball_by_ball"].append("LB1")
        
#     # Handle regular finger gestures
#     elif isinstance(gesture, int):
#         if gesture == 0:  # Fist - Wicket
#             if not state["free_hit"]:  # Can't get out on free hit (except run out)
#                 state["wickets"] += 1
#                 state["last_action"] = "WICKET!"
#                 state["ball_by_ball"].append("W")
#             else:
#                 state["last_action"] = "Free Hit - No Wicket (Dot Ball)"
#                 state["ball_by_ball"].append("•")
#             state["balls"] += 1
#             state["free_hit"] = False  # Free hit is over
            
#         elif gesture == 1:  # 1 finger - 1 run
#             state["runs"] += 1
#             state["balls"] += 1
#             if state["free_hit"]:
#                 state["last_action"] = "1 Run (Free Hit)"
#                 state["free_hit"] = False
#             else:
#                 state["last_action"] = "1 Run"
#             state["ball_by_ball"].append("1")
            
#         elif gesture == 2:  # 2 fingers - 2 runs
#             state["runs"] += 2
#             state["balls"] += 1
#             if state["free_hit"]:
#                 state["last_action"] = "2 Runs (Free Hit)"
#                 state["free_hit"] = False
#             else:
#                 state["last_action"] = "2 Runs"
#             state["ball_by_ball"].append("2")
            
#         elif gesture == 3:  # 3 fingers - 3 runs
#             state["runs"] += 3
#             state["balls"] += 1
#             if state["free_hit"]:
#                 state["last_action"] = "3 Runs (Free Hit)"
#                 state["free_hit"] = False
#             else:
#                 state["last_action"] = "3 Runs"
#             state["ball_by_ball"].append("3")
            
#         elif gesture == 4:  # 4 fingers - 4 runs
#             state["runs"] += 4
#             state["balls"] += 1
#             if state["free_hit"]:
#                 state["last_action"] = "4 Runs - Boundary (Free Hit)"
#                 state["free_hit"] = False
#             else:
#                 state["last_action"] = "4 Runs (Boundary)"
#             state["ball_by_ball"].append("4")
            
#         elif gesture == 5:  # 5 fingers - 6 runs (six)
#             state["runs"] += 6
#             state["balls"] += 1
#             if state["free_hit"]:
#                 state["last_action"] = "6 Runs - Six! (Free Hit)"
#                 state["free_hit"] = False
#             else:
#                 state["last_action"] = "6 Runs (Six!)"
#             state["ball_by_ball"].append("6")
    
#     # Handle over completion (only for legal deliveries)
#     if state["balls"] >= 6 and (state["balls"] % 6) == 0:
#         state["last_action"] += " - Over Complete!"
    
#     state["last_updated_fingers"] = gesture

# def reset_gesture_flag():
#     """Reset gesture flag when no hand is detected"""
#     state["last_updated_fingers"] = None

# def reset_match():
#     """Reset the entire match"""
#     state["runs"] = 0
#     state["wickets"] = 0
#     state["balls"] = 0
#     state["extras"] = 0
#     state["wides"] = 0
#     state["noballs"] = 0
#     state["byes"] = 0
#     state["legbyes"] = 0
#     state["last_updated_fingers"] = None
#     state["last_action"] = "Match Reset"
#     state["ball_by_ball"] = []
#     state["last_gesture_time"] = 0  # Reset cooldown timer
#     state["free_hit"] = False

# def undo_last_ball():
#     """Undo the last ball"""
#     if not state["ball_by_ball"]:
#         return
        
#     last_ball = state["ball_by_ball"].pop()
    
#     # Handle different types of deliveries
#     if last_ball == "W":
#         state["wickets"] = max(0, state["wickets"] - 1)
#         state["balls"] = max(0, state["balls"] - 1)
#     elif last_ball == "NB":
#         state["runs"] = max(0, state["runs"] - 1)
#         state["extras"] = max(0, state["extras"] - 1)
#         state["noballs"] = max(0, state["noballs"] - 1)
#         state["free_hit"] = False
#     elif last_ball == "WD":
#         state["runs"] = max(0, state["runs"] - 1)
#         state["extras"] = max(0, state["extras"] - 1)
#         state["wides"] = max(0, state["wides"] - 1)
#     elif last_ball == "B1":
#         state["runs"] = max(0, state["runs"] - 1)
#         state["extras"] = max(0, state["extras"] - 1)
#         state["byes"] = max(0, state["byes"] - 1)
#         state["balls"] = max(0, state["balls"] - 1)
#     elif last_ball == "LB1":
#         state["runs"] = max(0, state["runs"] - 1)
#         state["extras"] = max(0, state["extras"] - 1)
#         state["legbyes"] = max(0, state["legbyes"] - 1)
#         state["balls"] = max(0, state["balls"] - 1)
#     elif last_ball.isdigit() or last_ball == "•":
#         if last_ball.isdigit():
#             runs_to_subtract = int(last_ball)
#             state["runs"] = max(0, state["runs"] - runs_to_subtract)
#         state["balls"] = max(0, state["balls"] - 1)
    
#     state["last_action"] = f"Undid: {last_ball}"
#     state["last_updated_fingers"] = None






















# score_state.py
import streamlit as st
import time

# Global state dictionary
state = {
    "runs": 0,
    "wickets": 0,
    "balls": 0,  # Legal balls in current over (0-5)
    "extras": 0,  # Track extras separately
    "wides": 0,
    "noballs": 0,
    "byes": 0,
    "legbyes": 0,
    "last_updated_figures": None,
    "last_action": "Match Started",
    "ball_by_ball": [],
    "last_gesture_time": 0,
    "cooldown_period": 3.0,  # Reduced to 3 seconds cooldown
    "free_hit": False,  # Track if next ball is a free hit
    "innings": 1,  # Current innings (1 or 2)
    "first_innings_score": 0,
    "first_innings_wickets": 0,
    "first_innings_balls": 0,
    "match_overs": 20,  # Will be set from session state
    "match_complete": False,
    "winner": None
}

def get_score():
    """Get current match score"""
    overs = state["balls"] // 6
    balls_in_over = state["balls"] % 6
    
    # Calculate remaining cooldown time
    current_time = time.time()
    time_since_last = current_time - state["last_gesture_time"]
    cooldown_remaining = max(0, state["cooldown_period"] - time_since_last)
    
    return (state["runs"], state["wickets"], overs, balls_in_over, state["last_action"], 
            state["ball_by_ball"], cooldown_remaining, state["extras"], state["wides"], 
            state["noballs"], state["byes"], state["legbyes"], state["free_hit"], 
            state["innings"], state["first_innings_score"], state["match_complete"], state["winner"])

def update_score(gesture):
    """Update score based on gesture with cooldown"""
    current_time = time.time()
    
    # Check if we're still in cooldown period
    if current_time - state["last_gesture_time"] < state["cooldown_period"]:
        print(f"Gesture ignored - cooldown active")
        return  # Ignore gesture during cooldown
    
    # Check for duplicate gesture
    if state["last_updated_figures"] == gesture:
        print(f"Duplicate gesture ignored: {gesture}")
        return  # prevent duplicate score
    
    # Update the last gesture time and gesture
    state["last_gesture_time"] = current_time
    state["last_updated_figures"] = gesture
    
    print(f"Processing gesture: {gesture}")
    
    # Handle special gestures first
    if gesture == "no_ball":
        state["runs"] += 1  # No ball gives 1 run penalty
        state["extras"] += 1
        state["noballs"] += 1
        state["free_hit"] = True  # Next ball is a free hit
        state["last_action"] = "NO BALL! (+1 run, Free Hit next)"
        state["ball_by_ball"].append("NB")
        print(f"No Ball - Runs: {state['runs']}, Extras: {state['extras']}")
        # No ball doesn't count as a legal delivery, so don't increment balls
        
    elif gesture == "wide":
        state["runs"] += 1  # Wide gives 1 run penalty
        state["extras"] += 1
        state["wides"] += 1
        state["last_action"] = "WIDE! (+1 run)"
        state["ball_by_ball"].append("WD")
        print(f"Wide - Runs: {state['runs']}, Extras: {state['extras']}")
        # Wide doesn't count as a legal delivery, so don't increment balls
        
    elif gesture == "bye":
        # Byes don't add to batsman's score but add to team total
        state["runs"] += 1
        state["extras"] += 1
        state["byes"] += 1
        state["balls"] += 1  # Legal delivery
        state["last_action"] = "BYE! (+1 run)"
        state["ball_by_ball"].append("B1")
        print(f"Bye - Runs: {state['runs']}, Balls: {state['balls']}")
        
    elif gesture == "leg_bye":
        # Leg byes don't add to batsman's score but add to team total
        state["runs"] += 1
        state["extras"] += 1
        state["legbyes"] += 1
        state["balls"] += 1  # Legal delivery
        state["last_action"] = "LEG BYE! (+1 run)"
        state["ball_by_ball"].append("LB1")
        print(f"Leg Bye - Runs: {state['runs']}, Balls: {state['balls']}")
        
    elif gesture == "dot_ball":
        # Dot ball - no runs, but legal delivery
        state["balls"] += 1
        if state["free_hit"]:
            state["last_action"] = "Dot Ball (Free Hit)"
            state["free_hit"] = False
        else:
            state["last_action"] = "Dot Ball"
        state["ball_by_ball"].append("•")
        print(f"Dot Ball - Balls: {state['balls']}")
        
    # Handle regular finger gestures
    elif isinstance(gesture, int):
        if gesture == 0:  # Fist - Wicket
            if not state["free_hit"]:  # Can't get out on free hit (except run out)
                state["wickets"] += 1
                state["last_action"] = "WICKET!"
                state["ball_by_ball"].append("W")
            else:
                state["last_action"] = "Free Hit - No Wicket (Dot Ball)"
                state["ball_by_ball"].append("•")
            state["balls"] += 1  # Legal delivery
            state["free_hit"] = False  # Free hit is over
            print(f"Wicket/Dot - Wickets: {state['wickets']}, Balls: {state['balls']}")
            
        elif gesture == 1:  # 1 finger - 1 run
            state["runs"] += 1
            state["balls"] += 1  # Legal delivery
            if state["free_hit"]:
                state["last_action"] = "1 Run (Free Hit)"
                state["free_hit"] = False
            else:
                state["last_action"] = "1 Run"
            state["ball_by_ball"].append("1")
            print(f"1 Run - Runs: {state['runs']}, Balls: {state['balls']}")
            
        elif gesture == 2:  # 2 fingers - 2 runs
            state["runs"] += 2
            state["balls"] += 1  # Legal delivery
            if state["free_hit"]:
                state["last_action"] = "2 Runs (Free Hit)"
                state["free_hit"] = False
            else:
                state["last_action"] = "2 Runs"
            state["ball_by_ball"].append("2")
            print(f"2 Runs - Runs: {state['runs']}, Balls: {state['balls']}")
            
        elif gesture == 3:  # 3 fingers - 3 runs
            state["runs"] += 3
            state["balls"] += 1  # Legal delivery
            if state["free_hit"]:
                state["last_action"] = "3 Runs (Free Hit)"
                state["free_hit"] = False
            else:
                state["last_action"] = "3 Runs"
            state["ball_by_ball"].append("3")
            print(f"3 Runs - Runs: {state['runs']}, Balls: {state['balls']}")
            
        elif gesture == 4:  # 4 fingers - 4 runs
            state["runs"] += 4
            state["balls"] += 1  # Legal delivery
            if state["free_hit"]:
                state["last_action"] = "4 Runs - Boundary (Free Hit)"
                state["free_hit"] = False
            else:
                state["last_action"] = "4 Runs (Boundary)"
            state["ball_by_ball"].append("4")
            print(f"4 Runs - Runs: {state['runs']}, Balls: {state['balls']}")
            
        elif gesture == 5:  # 5 fingers - 6 runs (six)
            state["runs"] += 6
            state["balls"] += 1  # Legal delivery
            if state["free_hit"]:
                state["last_action"] = "6 Runs - Six! (Free Hit)"
                state["free_hit"] = False
            else:
                state["last_action"] = "6 Runs (Six!)"
            state["ball_by_ball"].append("6")
            print(f"6 Runs - Runs: {state['runs']}, Balls: {state['balls']}")
    
    # Handle over completion (only for legal deliveries)
    if state["balls"] > 0 and (state["balls"] % 6) == 0:
        state["last_action"] += " - Over Complete!"
        print(f"Over completed! Total balls: {state['balls']}")
    
    # Check for innings completion
    check_innings_completion()
    
    print(f"Final state - Runs: {state['runs']}, Wickets: {state['wickets']}, Balls: {state['balls']}")
    print(f"Ball by ball: {state['ball_by_ball']}")

def reset_gesture_flag():
    """Reset gesture flag when no hand is detected"""
    state["last_updated_figures"] = None

def set_match_overs(overs):
    """Set match overs from session state"""
    state["match_overs"] = overs

def reset_match():
    """Reset the entire match"""
    print("Resetting match...")
    state["runs"] = 0
    state["wickets"] = 0
    state["balls"] = 0
    state["extras"] = 0
    state["wides"] = 0
    state["noballs"] = 0
    state["byes"] = 0
    state["legbyes"] = 0
    state["last_updated_figures"] = None
    state["last_action"] = "Match Reset"
    state["ball_by_ball"] = []
    state["last_gesture_time"] = 0  # Reset cooldown timer
    state["free_hit"] = False
    state["innings"] = 1
    state["first_innings_score"] = 0
    state["first_innings_wickets"] = 0
    state["first_innings_balls"] = 0
    state["match_complete"] = False
    state["winner"] = None
    
    # Get match overs from session state if available
    try:
        import streamlit as st
        if 'match_overs' in st.session_state:
            state["match_overs"] = st.session_state.match_overs
    except:
        state["match_overs"] = 20  # Default to 20 overs

def undo_last_ball():
    """Undo the last ball"""
    if not state["ball_by_ball"]:
        print("No balls to undo")
        return
        
    last_ball = state["ball_by_ball"].pop()
    print(f"Undoing ball: {last_ball}")
    
    # Handle different types of deliveries
    if last_ball == "W":
        state["wickets"] = max(0, state["wickets"] - 1)
        state["balls"] = max(0, state["balls"] - 1)
    elif last_ball == "NB":
        state["runs"] = max(0, state["runs"] - 1)
        state["extras"] = max(0, state["extras"] - 1)
        state["noballs"] = max(0, state["noballs"] - 1)
        state["free_hit"] = False
    elif last_ball == "WD":
        state["runs"] = max(0, state["runs"] - 1)
        state["extras"] = max(0, state["extras"] - 1)
        state["wides"] = max(0, state["wides"] - 1)
    elif last_ball == "B1":
        state["runs"] = max(0, state["runs"] - 1)
        state["extras"] = max(0, state["extras"] - 1)
        state["byes"] = max(0, state["byes"] - 1)
        state["balls"] = max(0, state["balls"] - 1)
    elif last_ball == "LB1":
        state["runs"] = max(0, state["runs"] - 1)
        state["extras"] = max(0, state["extras"] - 1)
        state["legbyes"] = max(0, state["legbyes"] - 1)
        state["balls"] = max(0, state["balls"] - 1)
    elif last_ball == "•":  # Dot ball
        state["balls"] = max(0, state["balls"] - 1)
    elif last_ball.isdigit():
        runs_to_subtract = int(last_ball)
        if last_ball == "6":  # Six is worth 6 runs but shows as "6"
            runs_to_subtract = 6
        state["runs"] = max(0, state["runs"] - runs_to_subtract)
        state["balls"] = max(0, state["balls"] - 1)
    
    state["last_action"] = f"Undid: {last_ball}"
    state["last_updated_figures"] = None
    print(f"After undo - Runs: {state['runs']}, Wickets: {state['wickets']}, Balls: {state['balls']}")

def check_innings_completion():
    """Check if innings is complete and handle innings switch"""
    max_balls = state["match_overs"] * 6
    
    # First innings completion conditions
    if state["innings"] == 1 and (state["balls"] >= max_balls or state["wickets"] >= 10):
        # Store first innings data
        state["first_innings_score"] = state["runs"]
        state["first_innings_wickets"] = state["wickets"]
        state["first_innings_balls"] = state["balls"]
        
        # Start second innings
        state["innings"] = 2
        state["runs"] = 0
        state["wickets"] = 0
        state["balls"] = 0
        state["extras"] = 0
        state["wides"] = 0
        state["noballs"] = 0
        state["byes"] = 0
        state["legbyes"] = 0
        state["ball_by_ball"] = []
        state["free_hit"] = False
        
        target = state["first_innings_score"] + 1
        state["last_action"] = f"First Innings Complete! Target: {target} runs"
        
    # Second innings completion conditions
    elif state["innings"] == 2:
        target = state["first_innings_score"] + 1
        
        # Check if target achieved
        if state["runs"] >= target:
            state["match_complete"] = True
            state["winner"] = "chasing_team"
            balls_remaining = max_balls - state["balls"]
            state["last_action"] = f"Match Won! Target achieved with {balls_remaining} balls remaining!"
            
        # Check if innings complete without achieving target
        elif state["balls"] >= max_balls or state["wickets"] >= 10:
            state["match_complete"] = True
            if state["runs"] == state["first_innings_score"]:
                state["winner"] = "tie"
                state["last_action"] = "Match Tied!"
            else:
                state["winner"] = "defending_team"
                runs_short = target - state["runs"]
                state["last_action"] = f"Match Lost! Fell short by {runs_short} runs!"

def get_match_status():
    """Get current match status for display"""
    if state["innings"] == 1:
        return f"First Innings - {state['match_overs']} Overs"
    elif state["innings"] == 2 and not state["match_complete"]:
        target = state["first_innings_score"] + 1
        need = target - state["runs"]
        balls_left = (state["match_overs"] * 6) - state["balls"]
        return f"Second Innings - Need {need} runs in {balls_left} balls"
    else:
        return "Match Complete"