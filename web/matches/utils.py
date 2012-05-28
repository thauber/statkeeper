import models

def get_attempted_successful(side, action_type, actions):
    attempted = 0
    successful = 0
    for action in actions:
        if action.action_type == action_type \
            and action.actor \
            and action.actor.side == side:
            attempted += 1;
            for result in action.result_list:
                if result['type'] == "win" and result['winner'] == side:
                    successful += 1;
    return attempted, successful
