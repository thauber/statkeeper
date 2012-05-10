$(function() {
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
        if (this.options.match) {
            this.match = this.options.match
        } else {
            this.match = new SKMatch({},{
                leftPlayer: new SKPlayer(),
                rightPlayer: new SKPlayer()
            });
        }
        this.match.on('change:state', this.handleStateChange, this);
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
            if (!this.mapControl) {
                this.mapControl = new SKMapControlView({map: this.match.get("match_map")});
            }
            this.mapControl.setElement(this.$("#action-content"), true);
            this.mapControl.render();
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
    hideLoading: function() {
        if (this.loading) {
            this.loading = false;
            this.render();
        }
    }
});

SKMapControlView = Backbone.View.extend({
    tagName: 'div',
    events: {
        "click #map-view"        :"doCreateActionControlPopup",
        "click .action-control"  :"selectActionType",
        "click img.action"       :"clickAction",
        "click div.static-phase" :"editActionPhase",
        "click .action-delete"   :"deleteAction",
        "click .action-edit"     :"editAction", 
    },
    actionControlPopupTemplate: ESB.Template.make('SKActionControlPopup'),
    actionPopupTemplate: ESB.Template.make('SKActionPopup'),
    initialize: function() {
        this.map = this.options.map;
        this.actions = [];
    },
    render: function() {
        var actionViews = [];
        var container = $("<div id='map-container'>");
        
        //create the map
        var mapView = this.mapView = $("<img>");
        mapView.attr('src', this.map.url);
        mapView.attr('id', 'map-view');
        container.append(mapView);

        var i, length=this.actions.length, action, iconSrc, actionView;
        for (var i=0; i < length; i++) {
            action = this.actions[i];
            actionView = $("<img>");
            actionView.addClass("action");
            actionView.data('action-index', ""+i);

            actionView.attr('src', SKMapControlView.getIconForAction(action));
            actionView.css({
                left: action.get("position").x-10,
                top: action.get("position").y-10,
                position: 'absolute',
                width: 20,
                height: 20,
            });
            container.append(actionView);
        }
        if (this.phaser) {
            this.phaser.destroy();
        }
        if (this.selectedAction) {
            container.append(this.createActionPopup(this.selectedAction));
        } else if (this.controlPopup) {
            container.append(this.controlPopup);
        }
        $(this.el).html(container);
        return this.el;
    },
    doCreateActionControlPopup: function(evt) {
        position = {x:evt.offsetX, y:evt.offsetY};
        this.createActionControlPopup(position);
    },
    createActionControlPopup: function(position) {
        this.selectAction(null);
        this.controlPopup = $(this.actionControlPopupTemplate({
            actions: SKAction.Actions,
            position: position
        }))
        this.controlPopup.css({
            left: position.x+20,
            top: position.y-20,
            position: 'absolute'
        });
        this.render()
    },
    createActionPopup: function(action) {
        var position = action.get("position");
        this.phaser = this.getActionPhaser(action);
        this.phaser.on("phaser:change", function(evt){
            this.editablePhaseIndex = -1;
            this.render();
        }, this);
        this.phaser.on("phaser:close", this.unselectAction, this);
        var container = $(this.actionPopupTemplate({
            phaser: this.phaser,
            action: action,
            actionIndex: this.actions.indexOf(action),
            startedAt: ESB.Timer.displayClock(action.get("started_at")),
            finishedAt: ESB.Timer.displayClock(action.get("finished_at"))
        }));
        container.css({
            left: position.x+20,
            top: position.y-20,
            position: 'absolute',
            width: 200,
        });
        var phaseListContainer = container.find(".phase-list-container");
        var length=this.phaser.phases.length, i, phase;
        for (i=0; i < length; i++) {
            phase = this.phaser.phases[i];
            evenOrOdd = "even";
            if (i%2) {
                evenOrOdd = "odd";
            }
            var forceEditable = this.editablePhaseIndex == i;
            var editable = phase.editable || forceEditable;

            var phaseContainer = $("<div>")
                .addClass("phase")
                .addClass(evenOrOdd)
                .addClass(phase.className)
                .data("phase-index",i);
            if (!editable) {
                phaseContainer.addClass("static-phase");
            }
            phaseContainer.append(phase.html(forceEditable));
            phase.preparePhase(phaseContainer);

            if (phase.hidden) {
                phaseContainer.hide();
            }
            if (editable && phase.isFullScreen(forceEditable)) {
                return phaseContainer;
            }
            phaseListContainer.append(phaseContainer);
        }
        return container;
    },
    editActionPhase: function(evt) {
        var target = $(evt.target).closest("div.phase");
        this.editablePhaseIndex = parseInt(target.data('phase-index'));
        this.render();
    },
    unselectAction: function(phaser) {
        this.selectAction(null);
        this.render();
    },
    clickAction: function(evt) {
        var target = $(evt.target);
        var actionIndex = parseInt(target.data('action-index'));
        this.selectAction(this.actions[actionIndex]);
        this.render();
    },
    selectAction: function(action) {
        this.selectedAction = action;
        this.editablePhaseIndex = -1;
        this.editedActionIndex = null;
    },
    getActionPhaser: function(action) {
        switch (action.get("action_type")) {
            case SKAction.ActionMap.baseInvaded:
                return new SKBaseInvasionPhaser(action);
                break;
            case SKAction.ActionMap.engagement:
                return new SKEngagementPhaser(action);
                break;
            case SKAction.ActionMap.harassment:
                return new SKHarassmentPhaser(action);
                break;
        }
        return null;
    },
    deleteAction: function(evt) {
        var target = $(evt.target).closest('.action-delete')
        var confirmation = confirm(
            "Deleting an action can not be undone Do you wish to continue?"
        );
        if (confirmation) {
            this.actions.splice(parseInt(target.data("action-index")), 1);
            this.selectAction(null);
            this.render();
        }
    },
    editAction: function(evt) {
        var target = $(evt.target).closest('.action-edit')
        var confirmation = confirm(
            "Editing the action type will delete all entered information (the "+
            "time the action started will not change). Do you wish to continue?"
        );
        if (confirmation) {
            var actionIndex = parseInt(target.data("action-index"));
            var action = this.actions[actionIndex];
            this.createActionControlPopup(action.get("position"));
            this.editedActionIndex = actionIndex;
            this.render();
        }
    },
    selectActionType: function(evt) {
        this.controlPopup = null;
        var target = $(evt.target);
        var actionType = target.data('action-type');
        var side = target.data('action-side');
        var action;
        if (this.editedActionIndex != null) {
            var actionMap = SKAction.Actions;
            var i, length, actionData;
            for (i=0, length=actionMap.length; i < length; i++) {
                actionData = actionMap[i];
                if (actionData.action_type == actionType) {
                    break;
                }
            }
            action = this.actions[this.editedActionIndex];
            action.resetResults(actionData, actionType, side);
        } else {
            var position = {
                x:target.data('position-x'),
                y:target.data('position-y')
            };
            action = SKAction.createAction(
                actionType,
                side,
                position
            )
            this.actions.push(action);
        }
        this.selectAction(action);
        this.render();
    }
})
SKMapControlView.getIconForAction = function(action) {
   return SKActionIconMap[action.type] || SKActionIconMap.default;
}

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
