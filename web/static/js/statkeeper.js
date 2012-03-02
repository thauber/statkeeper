window.ESB = {};
Backbone.emulateJSON = true;

makeTestMatch = function() {
    var leftPlayer = new SKPlayer({race: 'protoss', name: 'Tony'})
    var rightPlayer = new SKPlayer({race: 'terran', name: 'Flo'})
    MatchView.match = new SKMatch(
        {state: 'started'},
        {leftPlayer:leftPlayer, rightPlayer: rightPlayer}
    )
    MatchView.leftPlayerView = null;
    MatchView.rightPlayerView = null;
    MatchView.controls = null;
    MatchView.render()
}

ESB.Template = {
    make: function (id) {
        return _.template($('#'+id).html());
    }
};
ESB.Util = {
    scrollToVisible: function (selector) {
        //TODO fix this
        var element = selector.first();
        var offset = element.offset();
        var scrollTo = offset.top-25;
        var body = $("body,html");
        var currentTop = body.scrollTop();
        if (currentTop < scrollTo) {
            body.animate({'scrollTop':scrollTo}, 40);
        }
    }
}
ESB.Timer = function(){
    this.time = 0;
    this.startTime = 0;
}
_.extend(ESB.Timer.prototype, Backbone.Events, {
    start: function() {
        this.startTime = new Date().getTime()/1000.0;
        window.setInterval(_.bind(this.tick, this), 1000)
    },
    tick: function() {
        this.time = (new Date().getTime()/1000) - this.startTime;
        this.trigger("tick", this)
    },
    displayClock: function() {
        return ESB.Timer.displayClock(this.time);
    }
});

ESB.Timer.displayClock = function(time){
    var minutes = Math.floor(time / 60);
    var seconds = Math.floor(time % 60);
    if (seconds < 10) {
        seconds = "0"+seconds;
    }
    if (minutes < 10) {
        minutes = "0"+minutes;
    }
    return "" + minutes + ":" + seconds;
};

$(function() {
SKMatch = Backbone.Model.extend({
    defaults: {
        winner: null,
        match_map: null,
    },
    initialize: function(attrs, options) {
        this.set("state", attrs['state'] || SKMatch.StateMap.unpublished);
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
    urlRoot: function() {
        var sidePart = this.side? ""+this.side+"/" : "";
        return "/matches/"+MatchView.match.id+"/player/"+sidePart;
    }
}); 

SKPlayer.races = {
    terran:"terran",
    protoss:"protoss",
    zerg:"zerg"
};

SKMatchView = Backbone.View.extend({
/*
 * This is the main root view. It is responsible for choosing the right view for the portions
 * of the view.
 */
    tmpl: ESB.Template.make('SKMatchView'),
    leftPlayer: {},
    rightPlayer: {},
    match: {},
    tagName: 'div',
    events: {
        "click #next-state-button a"    :"advanceState",
        "click .match-control-group a"  :"beginAction"
    },
    initialize: function() {
        this.match = new SKMatch({},{
            leftPlayer: new SKPlayer(),
            rightPlayer: new SKPlayer()
        });
        this.match.on('change:state', this.handleStateChange, this);
        this.match.on("sync", this.savePlayers, this);
        this.match.leftPlayer.on("sync", this.hideLoading, this);
        this.match.rightPlayer.on("sync", this.hideLoading, this);
        this.loading = false;
        this.defaultForces = {
            left: [],
            right: [],
        }
    },
    render: function() {
        $(this.el).html(
            this.tmpl({
                match: this.match,
                loading:this.loading
            })
        );
        this.prepareHeaderArea();
        
        if (this.match.get('state') == SKMatch.StateMap.started) {
            this.prepareActionArea();
        }

        return this.el;
    },
    prepareHeaderArea: function() {
        if (!this.leftPlayerView) {
            this.leftPlayerView = new SKPlayerView({
                match:this.match,
                player:this.match.leftPlayer,
                root:this
            })
        }
        if (!this.rightPlayerView) {
            this.rightPlayerView = new SKPlayerView({
                match:this.match,
                player:this.match.rightPlayer,
                root:this
            })
        }
        if (!this.controls) {
            this.controls = new SKMatchControls({
                match:this.match,
                root:this
            })
        }

        this.leftPlayerView.setElement(this.$("#player-left"), true);
        this.leftPlayerView.render();

        this.rightPlayerView.setElement(this.$("#player-right"), true);
        this.rightPlayerView.render();

        this.controls.setElement(this.$("#match-controls"), true);
        this.controls.render();
    },
    prepareActionArea: function () {
        if (this.currentActionView) {
            this.currentActionView.setElement(this.$("#action-content"), true);
            this.currentActionView.render();
        } else {
            if (!this.actionControls) {
                this.actionControls = new SKActionControlView({root: this});
            }
            this.actionControls.setElement(this.$("#action-content"), true);
            this.actionControls.render();
        }
    },
    /*
     * State of the match.
     *
     * All of these methods are responsible for advancing and setting the
     * state of the match: (unpublished, published, started, ended)
     */
    advanceState: function() {
        var shouldAdvance = true;
        switch(this.match.get("state")) {
            case 0:
                shouldAdvance = this.publish();
                break;
            case 1:
                shouldAdvance = this.start();
                break;
            case 2:
                shouldAdvance = this.end();
                break;
        }
        if (shouldAdvance) {
            this.match.set('state', SKMatch.nextState(this.match.get('state')));
        }
    },
    publish: function() {
        if (this.match.rightPlayer.get("name")
            && this.match.rightPlayer.get("race")
            && this.match.leftPlayer.get("name")
            && this.match.leftPlayer.get("race")) { 
            return true;
        }
        alert("You need to add a name and race for both players before you can publish");
        return false;
    },
    start: function() {
        MatchTimer.start()
        return true;
    },
    end: function() {
        //TODO modal asking who won.
        return confirm("Are you sure you want to end the game?")
    },

    /*
     * Begin Action
     *
     * This is called when an action control button is pressed to begin an
     * action.
     */
    beginAction: function(evt) {
        var side = $(evt.target).data('player');
        var actionID = $(evt.target).data('action');
        var actionName = $(evt.target).data('name');
        this.createActionView(SKAction.createAction(actionID, side));
        this.prepareActionArea();
    },
    createActionView: function(action) {
        this.setCurrentActionView(SKActionView.createActionView({
            action: action,
            match: this.match,
        }));

    },
    setCurrentActionView: function(nextActionView) {
        if (this.currentActionView) {
            this.currentActionView.off("finish");
            this.currentActionView.off("queue");
            this.currentActionView.off("cancel");
            this.currentActionView.destroy();
        }
        this.currentActionView = nextActionView;
        if (nextActionView) {
            this.currentActionView.on('finish', this.finishAction, this);
            this.currentActionView.on('queue', this.queueAction, this);
            this.currentActionView.on('cancel', this.cancelAction, this);
        }
    },
    
    /*
     * Status of current action
     *
     * All of these are callbacks from events on the current action view
     */
    finishAction: function(actionView) {
        this.trigger("finishAction", actionView.action);
        this.setCurrentActionView(null);
        this.prepareActionArea();
    },
    cancelAction: function(actionView) {
        this.setCurrentActionView(null);
        this.prepareActionArea();
    },
    queueAction: function(evt) {
        this.trigger("queueAction", this.currentActionView.action);
        this.setCurrentActionView(null);
        this.prepareActionArea();
    },

    /*
     * Queue interaction methods.
     *
     * Here are all of the methods involved in communicating with the
     * action queue.
     *
     * find:action-queue
     */
    setQueueView: function(queueView) {
        if (this.queueView) {
            this.queueView.off("dequeueAction");
            this.queueView.off("reinforceAction");
        }
        this.queueView = queueView;
        this.queueView.on("dequeueAction", this.dequeueAction, this);
        this.queueView.on("reinforceAction", this.dequeueAction, this);
    },
    dequeueAction: function(action) {
        if (this.currentActionView && this.currentActionView.action) {
            this.queueAction();
        }
        this.createActionView(action);
        this.prepareActionArea();
    },
    handleStateChange: function() {
        if (!this.match.id || !this.match.leftPlayer.id || !this.rightPlayer.id) {
            this.loading = true;
        }
        this.match.save();
        this.render();
    },
    savePlayers: function() {
        this.match.leftPlayer.save();
        this.match.rightPlayer.save();
    },
    hideLoading: function() {
        if (this.loading) {
            this.loading = false;
            this.render();
        }
    }
});

SKActionControlView = Backbone.View.extend({
    tmpl: ESB.Template.make('SKActionControlView'),
    tagName: 'div',
    initialize: function() {
        this.match = this.options.match;
        this.root = this.options.root;
    },
    render: function() {
        options = {
            playerActions: SKAction.playerActions,
            nonPlayerActions: SKAction.nonPlayerActions
        }
        $(this.el).html(
            this.tmpl(options)
        );
        return this.el;
    }
});

SKMatchControls = Backbone.View.extend({
/*
 * The view resposible for the clock and the buttons that progress the match
 * through the various states: unpublished, published, started, ended.
 *
 * Currently just the buttons
 */
    tmpl: ESB.Template.make('SKMatchControls'),
    tagName: 'div',
    initialize: function() {
        this.match = this.options.match;
        this.root = this.options.root;
        MatchTimer.on("tick", this.render, this);
    },
    render: function() {
        options = {
            match: this.match,
            timer: MatchTimer
        }
        $(this.el).html(
            this.tmpl(options)
        );
        return this.el;
    },
    updateTimer: function() {
        this.$(".timer").text(MatchTimer.displayClock());
    }
})

 
SKPlayerView = Backbone.View.extend({
/*
 * Responsible for all the information gathered about a player
 * Name, race, clan, starting position and color.
 *
 * It currently just handles Name and race.
 */
    tmpl: ESB.Template.make('SKPlayer'),
    raceListItemTmpl: ESB.Template.make('SKRace'),
    tagName: 'div',
    editable: true,
    initialize: function() {
        this.player = this.options.player || {};
        this.match = this.options.match;
    },
    render: function() {
        var state = this.match.get('state'),
            editable = state==SKMatch.StateMap.unpublished;
        options = {
            editable: editable,
            raceSelectedImg: null,
            size: 30,
            player: this.player
        };
        if (this.player.get("race")) {
            options.raceSelectedImg = ESB.RaceImgMap[this.player.get("race")];
        }
        $(this.el).html(
            this.tmpl(options)
        );
        var raceDropdown = $(this.el).find("._race_dropdown");
        var makeRaceListItem = _.bind(function (key, race) {
            raceLiOptions = {
                race: race,
                raceImg: ESB.RaceImgMap[race],
                thumbSize: 30
            }
            raceDropdown.append(this.raceListItemTmpl(raceLiOptions))
        }, this);
        _.each(SKPlayer.races, makeRaceListItem)
        if (editable) {
            $(this.el).addClass('editable');
            $(this.el).removeClass('uneditable');
        } else {
            $(this.el).addClass('uneditable');
            $(this.el).removeClass('editable');
        }
        return this.el;
    },
    raceUpdated: function(evt) {
        this.player.set("race", $(evt.target).data('race'));
        this.render();
    },
    nameUpdated: function(evt) {
        this.player.set("name", $(this.el).find('.player-name-input').val());
    },
    setEditable: function(editable) {
        this.editable = editable;
        this.render();
    },
    events: {
        "click ._race_option"           :"raceUpdated",
        "change .player-name-input"     :"nameUpdated"
    }
});
//Stupidly this has to be in a onload function
//But it's awful to read that way
});