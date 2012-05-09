SKMatch = Backbone.Model.extend({
    defaults: {
        winner: null,
        match_map: null,
    },
    initialize: function(attrs, options) {
        this.set("state", attrs['state'] || SKMatch.StateMap.published);
        this.leftPlayer = options.leftPlayer;
        this.leftPlayer.side = "left";
        this.rightPlayer = options.rightPlayer;
        this.rightPlayer.side = "right";
    },
    nextState: function() {
        var nextState = SKMatch.nextState(this.get("state"))
        if (!nextState) {
            throw "Matches can't advance to an invalid state. current state: "
                   + this.get('state');

        }
        this.set('state', nextState);
    },
    urlRoot: '/matches/'
}); 

SKAction = Backbone.Model.extend({
    /*
     * action_type
     * results
     * reinforcements_at
     * started_at
     * finished_at
     * position
     */
    initialize: function(attrs, options) {
        this.resetResults(options);
        this.on("sync", this.doQueuedSave, this);
        this.on("change:stage", this.queueSave, this);
    },
    resetResults: function(options, type, side) {
        if (side) {
            this.set("side", side);
        }
        if (type) {
            this.set("action_type", type);
        }
        this.name = options.name;
        this.set("changes_at", []);
        this.set("changes", []);
        this.set("results", []);
    },
    addResult: function(result, index) {
        this.get("results").splice(index, 1, result); 
    },
    addChange: function(change, time) {
        this.get("changes_at").push(time);
        this.get("changes").push(change);
    },
    urlRoot: function() {
        return "/matches/" + MatchView.match.id + "/actions/"
    },
    queueSave: function() {
        if (this.saving) {
            this.queued = true;
        } else {
            this.doQueuedSave();
        }
    },
    doQueuedSave: function() {
        this.queued = false;
        this.saving = true;
        unsetSaving = _.bind(function() {
            this.saving = false;
        }, this);
        var options = {
            success: unsetSaving,
            error: unsetSaving
        }
        this.save({}, options);
    },
    getActor: function() {
        if (this.get("side")=="left") {
            return BaseLeftPlayer;
        } else if (this.get("side")=="right") {
            return BaseRightPlayer;
        }
        return null;
    },
    getReceiver: function() {
        if (this.get("side")=="left") {
            return BaseRightPlayer;
        } else if (this.get("side")=="right") {
            return BaseLeftPlayer;
        }
        return null;
    },
    getActorsName: function() {
        var actor = this.getActor();
        if (actor) {
            return actor.get("name");
        }
        return null;
    },
    getWinnerInfo: function() {
        var results = this.get("results"), length=results.length, i, result;
        for (i=0; i<length; i++) {
            result = results[i];
            if (result.type == 'win') {
                break;
            }
        }
        if (result.winner=="left") {
            return [BaseLeftPlayer.get("name"), result.win_value];
        } else if (result.winner=="right") {
            return [BaseRightPlayer.get("name"), result.win_value];
        } else if (result.winner=="tie") {
            return ["tie", 0];
        }
        return ;
    }
}); 

SKAction.createAction = function(action_type, side, postion) {
//TODO add started to action
    var actions = SKAction.Actions;
    var i, length, action;
    for (i=0, length=actions.length; i < length; i++) {
        action = actions[i];
        if (action.action_type == action_type) {
            break;
        }
    }
    var actionAttrs = {
        started_at: MatchTimer.time,
        position: position,
    };
    if (side) {
        actionAttrs.side = side;
    }
    actionAttrs.action_type = action.action_type;
    if (!window.MatchActions) {
        window.MatchActions = [];
    }
    var actionObj = new SKAction(actionAttrs, action);
    window.MatchActions.push(actionObj);
    return actionObj;
}

SKAction.Stages = {
    inprogress  : "inprogress",   // Currently being worked on.
    reinforcing : "reinforcing",  // reinforcements are being added.
    queued      : "queued",       // Queued, but not complete.
    ongoing     : "ongoing",      // Some actions are ongoing like engagements.
    won         : "won",          // Game is won, but the winner has not been set.
    finished    : "finished",     // Completely done no more info needed.
    hidden      : "hidden"        // No longer showing up in the queue.
}

SKAction.ActionMap = {
    baseInvaded: "base_invaded",
    harassment: "harassment",
    engagement: "engagement"
}

SKAction.Actions = [
    {name:"Engagement", action_type:SKAction.ActionMap.engagement, sym: true},
    {name: "Invaded Base", action_type:SKAction.ActionMap.baseInvaded, sym:false},
    {name: "Harassment", action_type:SKAction.ActionMap.harassment, sym:false}
];

SKMatch.StateMap = {
     unpublished :"unpublished",
     published   :"published",
     started     :"started",
     ended       :"ended"
} 
SKMatch.States = [
    SKMatch.StateMap.unpublished,
    SKMatch.StateMap.published,
    SKMatch.StateMap.started,
    SKMatch.StateMap.ended
]

SKMatch.nextState = function(currentState) {
    currentIndex = SKMatch.States.indexOf(currentState)
    if (currentIndex < SKMatch.States.length-1) {
        return SKMatch.States[currentIndex+1];
    }
}

SKPlayer = Backbone.Model.extend({
/*    urlRoot: function() {
        var sidePart = this.side? ""+this.side+"/" : "";
        return "/matches/"+MatchView.match.id+"/player/"+sidePart;
    }
    */
}); 

SKPlayer.races = {
    terran:"terran",
    protoss:"protoss",
    zerg:"zerg"
};

