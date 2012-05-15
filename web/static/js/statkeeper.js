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
        "click .start-match"            : "start",
        "click .finish-match"           : "confirmFinish"
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
        this.matchStarted = this.match.get('started')
        if (this.matchStarted) {
            this.started();
        }
        this.matchFinished = this.match.get('finished')
        if (this.matchFinished) {
            this.finished();
        }
        this.match.on('sync', this.checkState, this);

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
        
        if (this.match.get('started')) {
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
    checkState: function() {
        if (this.match.get("started") && !this.matchStarted) {
            this.matchStarted = true;
            this.started();
        }
        if (this.match.get("finished") && !this.matchFinished) {
            this.matchStarted = true;
            this.finished();
        }
    },
    start: function() {
        this.match.set("started", true);
        this.match.save();
    },
    started: function() {
        MatchTimer.start()
        this.render();
    },
    confirmFinish: function() {
        //TODO FIX so that winner is chosen
        this.finish("left");
    },
    finish: function(winningSide) {
        winner = BaseLeftPlayer;
        if ("right") {
            winner = BaseRightPlayer
        }
        this.match.set({"finished": true, "winner":winner.get("player_id")});
        this.match.save();
    },
    finished: function() {
        this.render();
        //TODO stuff after finish
    }
});

SKMapControlView = Backbone.View.extend({
    tagName: 'div',
    events: {
        "click #map-view"               :"doCreateActionControlPopup",
        "click .action-control"         :"selectActionType",
        "click img.action"              :"clickAction",
        "click div.static-phase"        :"editActionPhase",
        "click .action-delete"          :"deleteAction",
        "click .action-edit"            :"editAction", 
        "click #other-action-controls"  :"doCreateOtherActionControlPopup",
        "click #remove-action-controls" :"removeActionControlPopup",
        "click .action-close"           :"removeActionPopup",
    },
    actionControlPopupTemplate: ESB.Template.make('SKActionControlPopup'),
    actionPopupTemplate: ESB.Template.make('SKActionPopup'),
    tmpl: ESB.Template.make('SKMapControlView'),
    initialize: function() {
        this.map = this.options.map;
        this.actions = [];
    },
    render: function() {
        var actionViews = [];
        var container = $(this.tmpl({
            mapURL: this.map.url,
            displayingControlPopup: this.controlPopup
        }));
        var i, length=this.actions.length, action, iconSrc, actionView;
        for (var i=0; i < length; i++) {
            action = this.actions[i];
            if (action.get("position")) {
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
        }
        if (this.phaser) {
            this.phaser.destroy();
        }
        if (this.selectedAction) {
            this.controlPopup = null;
            container.append(this.createActionPopup(this.selectedAction));
        } else if (this.controlPopup) {
            container.append(this.controlPopup);
        }
        $(this.el).html(container);
        return this.el;
    },
    removeActionControlPopup: function(evt) {
        this.controlPopup = null;
        this.render();
    },
    removeActionPopup: function(evt) {
        this.selectAction(null);
        this.render();
    },
    doCreateActionControlPopup: function(evt) {
        position = {x:evt.offsetX, y:evt.offsetY};
        this.createActionControlPopup(position);
    },
    doCreateOtherActionControlPopup: function(evt) {
        this.createActionControlPopup(null);
    },
    createActionControlPopup: function(position) {
        this.selectAction(null);
        this.controlPopup = $(this.actionControlPopupTemplate({
            actions: SKAction.Actions,
            position: position,
        }))
        if (position) {
            this.controlPopup.css({
                left: position.x+20,
                top: position.y-20,
            });
        }
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
        if (position) {
            container.css({
                left: position.x+20,
                top: position.y-20,
            });
        }
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
            case SKAction.ActionMap.unit_creation:
                return new SKUnitCreationPhaser(action);
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
            var position = null;
            if (target.data('position-x') || target.data('position-y')) {
                var position = {
                    x:target.data('position-x'),
                    y:target.data('position-y')
                };
            }
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
    initialize: function() {
        this.player = this.options.player || {};
        this.match = this.options.match;
    },
    render: function() {
        var options = {
            player: this.player,
            size: 30,
            raceSelectedImg:  ESB.RaceImgMap[this.player.get("race")]
        };
        $(this.el).html(
            this.tmpl(options)
        );
        return this.el;
    },
});
//Stupidly this has to be in a onload function
//But it's awful to read that way
});
