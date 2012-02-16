window.ESB = {};
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
    states: ['unpublished', 'published', 'started', 'ended'],
    defaults: {
        state: 0,
    },
    nextState: function() {
        if (this.get('state') == this.states.length-1) {
            throw "Matches can't advance to an invalid state. current state: "
                   + this.states[this.get('state')];

        }
        this.set('state', this.get('state')+1);
    }
}); 




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
        this.match = new SKMatch();
        this.match.on('change:state', this.render, this);
    },
    render: function() {
        $(this.el).html(
            this.tmpl({
                match: this.match
            })
        );
        this.prepareHeaderArea();
        
        if (this.match.get('state') == 2) {
            this.prepareActionArea();
        }

        return this.el;
    },
    prepareHeaderArea: function() {
        if (!this.leftPlayerView) {
            this.leftPlayerView = new SKPlayerView({
                match:this.match,
                player:this.leftPlayer,
                root:this
            })
        }
        if (!this.rightPlayerView) {
            this.rightPlayerView = new SKPlayerView({
                match:this.match,
                player:this.rightPlayer,
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
            this.match.set('state', this.match.get('state')+1);
        }
    },
    publish: function() {
        if (this.rightPlayer.name
            && this.rightPlayer.race
            && this.leftPlayer.name
            && this.leftPlayer.race) { 
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
            left: this.leftPlayer,
            right: this.rightPlayer
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
        this.render();
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
 * through the various stages: unpublished, published, started, ended.
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
    races: ["terran","protoss","zerg"],
    initialize: function() {
        this.player = this.options.player || {};
        this.match = this.options.match;
    },
    render: function() {
        var state = this.match.get('state'),
            editable = state==0;
        options = {
            editable: editable,
            raceSelectedImg: null,
            size: 30,
            player: this.player
        };
        if (this.player.race) {
            options.raceSelectedImg = ESB.RaceImgMap[this.player.race];
        }
        $(this.el).html(
            this.tmpl(options)
        );
        var raceDropdown = $(this.el).find("._race_dropdown");
        var makeRaceListItem = _.bind(function (race) {
            raceLiOptions = {
                race: race,
                raceImg: ESB.RaceImgMap[race],
                thumbSize: 30
            }
            raceDropdown.append(this.raceListItemTmpl(raceLiOptions))
        }, this);
        _.each(this.races, makeRaceListItem)
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
        this.player.race = $(evt.target).data('race');
        this.render();
    },
    nameUpdated: function(evt) {
        this.player.name = $(this.el).find('.player-name-input').val()
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
