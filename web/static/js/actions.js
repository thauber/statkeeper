$(function() {

/*
 * Phases
 */
SKPhase = function(action) {
    this.editable = true;
    this.hidden = true;
    this.action = action;
    this.initialize.apply(this, arguments);
}
_.extend(SKPhase.prototype, Backbone.Events, {
    type:null,
    initialize:function() {},
    _setup:function(data) {
        if (data.type == this.type) {
            this.setup(data);
        }
    },
    isFullScreen:function(forceEditable) {
        return false;
    },
    setup:function(data) {
        this.data = data;
    },
    preparePhase:function(view) {
        view.delegate("[data-control='end']", 'click', _.bind(function(evt) {
            this.trigger('phase:end', this, view);
        },this));
            
        view.delegate("[data-control='change']", 'click', _.bind(function(evt) {
            var target = $(evt.target);
            this.trigger('phase:change', this, target.data("change"));
        },this));
    },
    endPhase:function(view) {},    
    html: function() {},
});
SKPhase.extend = Backbone.Model.extend;

SKForcesPhase = SKPhase.extend({
    initialize: function(action, player, header, armory) {
        this.player = player;
        this.header = header;
        this.armory = armory;
    },
    endPhase: function() {
        var results = this.compositionPane.finish()
        return {'type': 'forces', 'forces':results}
    },
    type: "forces",
    isFullScreen: function(forceEditable) {
        return this.editable || forceEditable;
    },
    html: function(forceEditable) {
        if (this.editable || forceEditable) {
            this.compositionPane = new SKPaneUnitComposition({
                player: this.player,
                armory: this.armory,
                initialData: this.data && this.data.forces,
            });
            tmpl = ESB.Template.make('SKForcesPhase');
            var fullscreen = $(tmpl({header: this.header})).addClass("fullscreen");
            this.compositionPane.setElement(fullscreen.find(".forces"));
            this.compositionPane.render();
            return fullscreen;
        } else {
            return $("<p>Forces have been added</p>");
        }
    }
});
SKOngoingPhase = SKPhase.extend({
    breakFirst:true,
    endPhase:function(view) {
        this.action.set("finished_at", MatchTimer.time);
    },    
    html: function() {
        return $("#SKOngoingPhase").html();
    },
});

SKWinPhase = SKPhase.extend({
    initialize: function(){
        this.value = 3;
    },
    type: "win",
    setup: function(data) {
        var adjuster = 0;
        if (data.winner == "tie") {
            this.value = 3;
        } else if (data.winner == "left") {
            this.value = 3 - data.win_value;
        } else if (data.winner == "right") {
            this.value = 3 + data.win_value;
        }
    },
    preparePhase: function(view) {
        view.find(".win-bar").slider({
            value: this.value,
            range: "min",
            min: 0,
            max: 6,
            step: 1,
            change: _.bind(function(evt, ui) {
                this.value = ui.value;
                this.trigger('phase:end', this, view);
            },this)
        });
    },
    endPhase: function(view) {
        var winner, winValue;
        if (this.value < 3) {
            winner = "left";
            winValue = 3 - this.value;
        } else if (this.value > 3) {
            winner = "right";
            winValue = this.value - 3;
        } else { 
            winner = "tie";
            winValue = 3;
        }
        return {'type': 'win', 'winner': winner, 'win_value': winValue};
    },
    html: function(forceEditable) {
        if (this.editable || forceEditable) {
            return ESB.Template.make("SKWinPhase")({
                leftPlayerName: BaseLeftPlayer.get("name"),
                rightPlayerName: BaseRightPlayer.get("name")
            });
        } else {
            var winnerInfo = this.action.getWinnerInfo(), text;
            var victoryMap = {
                3: "won decisively",
                2: "won moderately",
                1: "won barely"
            }
            if (winnerInfo && winnerInfo[0] == "tie") {
                text = "Both players tied";
            } else if (winnerInfo) {
                text = winnerInfo[0] + " " + victoryMap[winnerInfo[1]];
            } else {
                text = "Unknown";
            }
            return $("<p>"+text+"</p>");
        }
    }
})

SKReengagePhase = SKPhase.extend({
    breakFirst: true,
    endPhase: function(view) {
        var results = this.action.get("results"), length=results.length, i, result;
        for (i=0; i<length; i++) {
            result = results[i];
            if (result.type == 'win') {
                results.splice(i,1);
            }
        }
        this.action.unset("finished_at");
    },
    html: function() {
        return $("#SKReengagePhase").html();
    }
})


/*
 * Phasers
 */
SKPhaser = function(action){
    this.action = action;
    this.initialize.apply(this, arguments);
    this.makePhases();
    this._addPhaseListeners();
    this._insertData();
}
_.extend(SKPhaser.prototype, Backbone.Events, {
    initialize: function(action){},
    adjustForChanges: function(action){},
    _addPhaseListeners: function() {
        var phase, length=this.phases.length, i;
        for (i=0; i<length; i++) {
            phase = this.phases[i];
            phase.on('phase:end', function(phase, view) {
                this.endPhase(phase, view);
            }, this);
            phase.on('phase:change', this.changePhase, this);
        }
    },
    _insertData: function() {
        var length=this.phases.length, lastShown=true, phase, i, data;
        for (i=0; i<length; i++) {
            phase = this.phases[i];
            data = this.action.get("results")[i]
            if (data && data.type == phase.type) {
                phase.setup(data);
                phase.hidden = false;
                phase.editable = false;
                lastShown = true;
            } else if (data) {
                phase.hidden = false;
                phase.editable = false;
                lastShown = true;
            } else if (lastShown) {
                lastShown = false;
                phase.hidden = false;
                phase.editable = true;
            } else {
                phase.hidden = true;
            }
        }
    },
    startPhase: function(nextPhase) {
        if (nextPhase && !nextPhase.breakFirst) {
            this.trigger('phaser:change', this);
        } else {
            this.trigger('phaser:close', this);
        }
    },
    changePhase: function(phase, change) {
        this.action.addChange(change, MatchTimer.time);
        this.trigger('phaser:change', this);
    },
    endPhase: function(phase, view) {
        var info = phase.endPhase(view);
        var index = this.getPhaseIndex(phase);
        if (this.action.get("results").length > index) {
            this.action.get("results")[index] = info;
        } else {
            this.action.get("results").push(info);
        }
        this.action.save();
        var nextPhase = this.getNextPhase(phase); 
        this.startPhase(nextPhase);
    },
    getNextPhase: function(phase) {
        var test, length=this.phases.length, i;
        for (i=0; i<length; i++) {
            test = this.phases[i];
            if (test == phase && i < length-1) {
                return this.phases[i+1];
            }
        }
        return null;
    },
    getPhaseIndex: function(phase) {
        var test, length=this.phases.length, i;
        for (i=0; i<length; i++) {
            test = this.phases[i];
            if (test == phase) {
                return i;
            }
        }
        return null;
    },
    destroy: function() {
        var phase, length=this.phases.length, i;
        for (i=0; i<length; i++) {
            phase = this.phases[i];
            phase.off('phase:end');
            this.off('phaser:close');
            this.off('phaser:change');
        }
    }
});
SKPhaser.extend = Backbone.Model.extend;

SKEngagementPhaser = SKPhaser.extend({
    makePhases: function() {
        var forcePhases = this.getForcePhases()
        this.phases = forcePhases;
        var i, length=this.action.get("changes").length, change;
        for (i=0; i < length; i++) {
            this.phases = this.phases.concat(this.getForcePhases(true));
        }
        if (this.action.get("finished_at")==null) {
            this.phases.push(new SKOngoingPhase(this.action));
        }
        this.phases.push(new SKWinPhase(this.action));
        this.phases.push(new SKReengagePhase(this.action));
    },
    getForcePhases: function(reinforcements) {
        var player1 = BaseLeftPlayer;
        var player2 = BaseRightPlayer;
        var player1Header = player1.get("name") + "'s Army";
        var player2Header = player2.get("name") + "'s Army";
        if (reinforcements) {
            player1Header = player1.get("name") + "'s Reinforcements";
            player2Header = player2.get("name") + "'s Reinforcements";
        }
        return [
            new SKForcesPhase(
                this.action,
                player1,
                player1Header,
                {
                    units: SKArmoryView.Units[player1.get("race")]
                }
            ),
            new SKForcesPhase(
                this.action,
                player2,
                player2Header,
                {
                    units: SKArmoryView.Units[player2.get("race")]
                }
            ),
        ];
    }
});
SKBaseInvasionPhaser = SKEngagementPhaser.extend({
    getForcePhases: function(reinforcements) {
        var player1 = this.action.getActor();
        var player2 = this.action.getReceiver();
        var player1Header = player1.get("name") + "'s Army";
        var player2Header = player2.get("name") + "'s Defense";
        if (reinforcements) {
            player1Header = player1.get("name") + "'s Reinforcements";
            player2Header = player2.get("name") + "'s Reinforcements";
        }
        return [
            new SKForcesPhase(
                this.action,
                player1,
                player1Header,
                {
                    units: SKArmoryView.Units[player1.get("race")],
                    structures: SKArmoryView.Structures[player1.get("race")]
                }
            ),
            new SKForcesPhase(
                this.action,
                player2,
                player2Header,
                {
                    units: SKArmoryView.Units[player2.get("race")],
                    structures: SKArmoryView.Structures[player2.get("race")]
                }
            ),
        ];
    }
});
SKHarassmentPhaser = SKEngagementPhaser.extend({
    getForcePhases: function(reinforcements) {
        var player1 = this.action.getActor();
        var player2 = this.action.getReceiver();
        var player1Header = player1.get("name") + "'s Harassment";
        var player2Header = player2.get("name") + "'s Defense";
        if (reinforcements) {
            player1Header = player1.get("name") + "'s Reinforcements";
            player2Header = player2.get("name") + "'s Reinforcements";
        }
        return [
            new SKForcesPhase(
                this.action,
                player1,
                player1Header,
                {
                    units: SKArmoryView.Units[player1.get("race")],
                    structures: SKArmoryView.Structures[player1.get("race")]
                }
            ),
            new SKForcesPhase(
                this.action,
                player2,
                player2Header,
                {
                    units: SKArmoryView.Units[player2.get("race")],
                    structures: SKArmoryView.Structures[player2.get("race")]
                }
            ),
        ];
    }
});

SKActionView = Backbone.View.extend({
/*
 * The base view.  Subclasses of this will define action panel
 * sequences.  Each action panel in the sequence will be shown
 * in order.
 */
    tmpl: ESB.Template.make('SKActionView'),
    initialize: function() {
        this.action = this.options.action;
        this.match = this.options.match;
        this.actor = this.options.actor;
        this.receiver = this.options.receiver;
        this.paneIndex = 0;
        this.buildPanes();
        this.restoreResults();
        this.currentPane = this.panes[this.paneIndex];
    },
    events: {
        'click #next-pane'  : "nextPane",
        'click #prev-pane'  : "prevPane",
        'click #queue'      : "queue",
        'change .story'     : "storeStory"
    },
    render: function() {
        var prevButtonText = "Back";
        var nextButtonText = "Next";
        var prevButtonClass = "";
        var nextButtonClass = "";
        if (this.paneIndex == this.panes.length-1) {
            nextButtonClass = "btn-success";
            nextButtonText = "Finish";
        } else if (this.paneIndex == 0) {
            prevButtonClass = "btn-danger";
            prevButtonText = "Cancel";
        }
        options = {
            action: this.action,
            story: this.story,
            nextButtonText: this,
            prevButtonText: prevButtonText,
            nextButtonText: nextButtonText,
            prevButtonClass: prevButtonClass,
            nextButtonClass: nextButtonClass
        }
        $(this.el).html(
            this.tmpl(options)
        );
        if (this.currentPane) {
            this.currentPane.setElement(this.$('#action-pane'), true);
            this.currentPane.render();
        }

        return this.el;
    },
    nextPane: function(evt) {
        var result = this.currentPane.finish();
        if(result) {
            this.action.addResult(result, this.paneIndex);
            if(this.paneIndex == this.panes.length-1) {
                this.finish();
            } else {
                this.paneIndex++;
                this.currentPane = this.panes[this.paneIndex];
                this.render();
            }
        }
    },
    prevPane: function() {
        if(this.paneIndex == 0) {
            this.cancel();
        } else {
            this.paneIndex--;
            this.currentPane = this.panes[this.paneIndex];
            this.render();
        }
    },
    queue: function() {
        this.trigger("queue", this)
    },
    finish: function() {
        this.trigger("finish", this)
    },
    cancel: function() {
        this.trigger("cancel", this)
    },
    storeStory: function() {
        this.story = this.$('.story').val()
    },
    restoreResults: function() {
        var i, length, pane, result;
        for (i=0, length=this.action.get("reinforcements_at").length; i < length; i++) {
            this.panes = this.panes.concat(this.createReinforcementPanes());
        }
        for (i=0, length=this.action.get("results").length; i < length; i++) {
            pane = this.panes[i];
            result = this.action.get("results")[i];
            pane.setResult(result);
        }
        this.paneIndex = Math.min(this.action.get("results").length, this.panes.length-1);
    },
    destroy: function() {
        this.undelegateEvents();
    }
});

SKActionView.createActionView = function(options) {
    var side = options.action.get('side');
    options.actor = options.match.rightPlayer;
    options.receiver = options.match.leftPlayer;
    if (side == "left") {
        options.actor = options.match.leftPlayer;
        options.receiver = options.match.rightPlayer;
    }
    switch (options.action.get('action_type')) {
        case SKAction.ActionMap.baseBuilt:
            return new SKActionBaseBuilt(options);
        case SKAction.ActionMap.baseDestroyed:
            return new SKActionBaseDestroyed(options);
        case SKAction.ActionMap.baseDestroyed:
            return new SKActionBaseInvaded(options);
        case SKAction.ActionMap.baseInvaded:
            return new SKActionHarassment(options);
        case SKAction.ActionMap.harassment:
            return new SKActionMacro(options);
        case SKAction.ActionMap.engagement:
            return new SKActionEngagement(options);
    }
}

/* Actions */
SKActionBaseInvaded = SKActionView.extend({
    buildPanes: function() {
        this.panes = [
            new SKPaneUnitComposition({
                title: this.actor.get("name") + "'s Army",
                player: this.actor,
                armory: {
                    units: SKArmoryView.Units[this.actor.get("race")]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.get("name") + "'s Defenses",
                player: this.receiver,
                armory: {
                    units: SKArmoryView.Units[this.receiver.get("race")],
                    structures: SKArmoryView.Structures[this.receiver.get("race")]
                }
            })
        ];
    },
    createReinforcementPanes: function() {
        return [
            new SKPaneUnitComposition({
                title: this.actor.get("name") + "'s Reinforcements",
                player: this.actor,
                armory: {
                    units: SKArmoryView.Units[this.actor.get("race")]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.get("name") + "'s Reinforcements",
                player: this.receiver,
                armory: {
                    units: SKArmoryView.Units[this.receiver.get("race")],
                    structures: SKArmoryView.Structures[this.receiver.get("race")]
                }
            })
        ];
    }
});

SKActionHarassment = SKActionView.extend({
    buildPanes: function() {
        this.panes = [
            new SKPaneUnitComposition({
                title: this.actor.get("name") + "'s Harassment",
                player: this.actor,
                armory: {
                    units: SKArmoryView.Units[this.actor.get("race")]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.get("name") + "'s Defenses",
                player: this.receiver,
                armory: {
                    units: SKArmoryView.Units[this.receiver.get("race")],
                    structures: SKArmoryView.Structures[this.receiver.get("race")]
                }
            })
        ];
    },
    createReinforcementPanes: function() {
        return [
            new SKPaneUnitComposition({
                title: this.actor.get("name") + "'s Reinforcements",
                player: this.actor,
                armory: {
                    units: SKArmoryView.Units[this.actor.get("race")]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.get("name") + "'s Reinforcements",
                player: this.receiver,
                armory: {
                    units: SKArmoryView.Units[this.receiver.get("race")],
                    structures: SKArmoryView.Structures[this.receiver.get("race")]
                }
            })
        ];
    }
});

/*
SKActionMacro = SKActionView.extend({
    buildPanes: function() {
        this.panes = []
    }
});
*/

SKActionEngagement = SKActionView.extend({
    buildPanes: function() {
        this.panes = [
            new SKPaneUnitComposition({
                title: this.match.leftPlayer.get("name") + "'s Army",
                player: this.match.leftPlayer,
                armory: {
                    units: SKArmoryView.Units[this.match.leftPlayer.get("race")]
                }
            }),
            new SKPaneUnitComposition({
                title: this.match.rightPlayer.get("name") + "'s Army",
                player: this.match.rightPlayer,
                armory: {
                    units: SKArmoryView.Units[this.match.rightPlayer.get("race")]
                }
            })
        ];
    },
    createReinforcementPanes: function() {
        return [
            new SKPaneUnitComposition({
                title: this.match.leftPlayer.get("name") + "'s Reinforcements",
                player: this.match.leftPlayer,
                armory: {
                    units: SKArmoryView.Units[this.match.leftPlayer.get("race")]
                }
            }),
            new SKPaneUnitComposition({
                title: this.match.rightPlayer.get("name") + "'s Reinforcements",
                player: this.match.rightPlayer,
                armory: {
                    units: SKArmoryView.Units[this.match.rightPlayer.get("race")]
                }
            })
        ];
    }
});

/* Panes and accessories */

SKPane = Backbone.View.extend({
    render: function() {
        $(this.el).html(
            this.tmpl(this.options)
        );
    }
});
SKPaneSupplyUpdate = SKPane.extend({
    tmpl: ESB.Template.make('SKPaneSupplyUpdate')
});

SKPanePositioning = SKPane.extend({
    tmpl: ESB.Template.make('SKPanePositioning')
});

SKPaneUnitComposition = SKPane.extend({
    tmpl: ESB.Template.make('SKPaneUnitComposition'),
    initialize: function() {
        this.quantities = [];
        this.player = this.options.player
        if (this.options.initialData) {
            this.setResult(this.options.initialData);
        }
        defaults = SKUnitDefaultManager.getDefaults(this.player);
        this.setResult(defaults)
    },
    render: function() {
        var options = {
            title: this.options.title || "Composition"
        }
        $(this.el).html(
            this.tmpl(options)
        );

        var i, length, quantity;
        for (i=0, length=this.quantities.length; i < length; i++) {
            quantity = this.quantities[i]
            this.$("#quantities").append(quantity.render());
        }
        if (!this.armory) {
            this.armory = new SKArmoryView(this.options.armory);
            this.armory.on("elementSelected", this.addQuantity, this);
        }
        this.armory.setElement(this.$("#armory"), true);
        this.armory.render();
        this.$(".armory-search").focus();

        return this.el;
    },
    getQuantity: function(type) {
        var i, length, quantity, sameQuantity;
        for (i=0, length=this.quantities.length; i < length; i++) {
            quantity = this.quantities[i]
            if (quantity.type == type) {
                sameQuantity=quantity;
            }
        }
        return sameQuantity;
    },
    addQuantity: function(element) {
        var sameQuantity = this.getQuantity(element);
        if (sameQuantity) {
            //TODO scroll to element if its not visible
            sameQuantity.shake();
        } else {
            SKUnitDefaultManager.addDefault(element, this.player);
            this.createQuantity(element);
            this.render();
        }
    },
    createQuantity: function(element) {
        var newQuantity = new SKArmoryQuantityView({type:element});
        newQuantity.on('remove', this.removeQuantity, this);
        this.quantities.push(
            newQuantity
        )
        return newQuantity;
    },
    removeQuantity: function(quantityToRemove) {
        var i, length, quantity;
        for (i=0, length=this.quantities.length; i<length; i++) {
            quantity = this.quantities[i];
            if (quantityToRemove == quantity) {
                this.quantities.splice(i,1);
                quantity.off("remove");
                break;
            }
        }
        SKUnitDefaultManager.removeDefault(quantity.type, this.player);
        this.render();
    },
    finish: function() {
        var results = [];
        var i, length, quantity;
        for (i=0, length=this.quantities.length; i<length; i++) {
            quantity = this.quantities[i];
            if (quantity.estimate!=null) {
                results.push({
                    type: quantity.type,
                    estimate: quantity.estimate
                });
            } else {
                quantity.shake();
                return false
            }
        }
        return results;
    },
    setResult: function(resultList) {
        var i, length, result, quantity, isAddable, sameQuantity, 
            addables, addableLength;
        addables = [];
        for (var armoryKey in this.options.armory) {
            addables = addables.concat(this.options.armory[armoryKey]);
        }
        for (i=0, length=resultList.length; i<length; i++) {
            result = resultList[i];
            sameQuantity = this.getQuantity(result.type)
            
            isAddable = false;
            for (j=0, addableLength=addables.length; j<addableLength; j++) {
                if (addables[j]==result.type) isAddable=true;
            }
            if (isAddable && !sameQuantity) {
                quantity = this.createQuantity(result.type);
                quantity.estimate = result.estimate;
            }
        }
    }
});

SKActionQueueView = Backbone.View.extend({
    tmpl: ESB.Template.make('SKActionQueueView'),
    initialize: function() {
        this.actions = [];
    },
    events: {
        'click .queue-action .btn': "handleAdvanceStage"
    },
    render: function() {
        var i, length, action, actionOptionsList = [];
        for (i=0, length=this.actions.length; i < length; i++) {
            action = this.actions[i]
            actionOptionsList.push(this.getActionOptions(action));
        }
        var options = {
            actionOptionsList: actionOptionsList       
        };
        $(this.el).html(
            this.tmpl(options)
        );
        this.$(".win-bar").slider({
            value: 3,
            range: "min",
            min: 0,
            max: 6,
            step: 1,
            slide: _.bind(function(evt, ui) {
                var index = $(evt.target).data('action-index');
                var action = this.actions[parseInt(index)];
                action.winValue = ui.value;
            },this)
        });

        return this.el;
    },
    getActionIndex: function(action) {
        var i, length;
        for (i=0, length=this.actions.length; i < length; i++) {
            if (this.actions[i] == action) {
                return i;
            }
        }
    },
    getActionOptions: function(action) {
        switch(action.get('stage')) {
            case SKAction.Stages.queued:
                return {
                    buttons: [{stage: SKAction.Stages.inprogress, text: "Work On"}],
                    statusText: "Queued...",
                    action: action
                }
            case SKAction.Stages.ongoing:
                var finishAction;
                if (action.battle) {
                    finishAction = SKAction.Stages.won;
                } else {
                    finishAction = SKAction.Stages.finished;
                }
                return {
                    buttons: [
                        {stage: SKAction.Stages.inprogress, text: "Work On"},
                        {stage: SKAction.Stages.reinforcing, text: "Reinforce"},
                        {stage: finishAction, text: "Finish"}
                    ],
                    statusText: "Ongoing...",
                    action: action
                }
            case SKAction.Stages.won:
                return {
                    statusText: "Finshed...",
                    action: action
                }
            case SKAction.Stages.finished:
                return {
                    buttons: [
                        {stage: SKAction.Stages.inprogress, text: "Work On"},
                        {stage: SKAction.Stages.ongoing, text: "Re-engage"},
                        {stage: SKAction.Stages.hidden, text: "Hide"}
                    ],
                    statusText: "Finished...",
                    action: action
                }
        }
    },
    handleAdvanceStage: function(evt) {
        var button = $(evt.target);
        var stage = button.data('stage');
        var index = button.data('action-index');
        var action = this.actions[index];
        this.advanceStage(action, stage, index);
    },
    advanceStage: function(action,stage,index) {
        switch (stage) {
            case SKAction.Stages.inprogress:
                this.actions.splice(index, 1);
                this.trigger("dequeueAction", action);
                break;
            case SKAction.Stages.reinforcing:
                this.actions.splice(index, 1);
                action.addReinforcements(MatchTimer.time);
                this.trigger("reinforceAction", action);
                break;
            case SKAction.Stages.finished:
                var winner;
                var winValue;
                if (action.battle) {
                    if (action.winValue == 3) {
                        winner = "tie";
                        winValue = 0;
                    } else if (action.winValue > 3) {
                        winner = "left";
                        winValue = action.winValue -3
                    } else {
                        winner = "right";
                        winValue = (action.winValue - 3) * -1
                    }
                    action.set("win_value", winValue);
                    action.set("winner", winner);
                }
                var autohideAction = _.bind(function() {
                    $('#action-'+action.id).hide(
                        50, 
                        _.bind(function() {
                            var index = this.getActionIndex(action);
                            var stage = SKAction.Stages.hidden;
                            if (index!=null) {
                                this.advanceStage(action, stage, index);
                            }
                        }, this)
                    )
                }, this);
                setTimeout(autohideAction, 5000);
            case SKAction.Stages.won:
                action.set("finished_at", MatchTimer.time);
                break;
            case SKAction.Stages.ongoing:
                action.unset("win_value");
                action.set("winner");
                break;
            case SKAction.Stages.hidden:
                this.actions.splice(index, 1);
                break;
            default:
        }
        action.set("stage", stage);
        this.render();
    },
    /*
     * Match interaction methods.
     *
     * Here are all of the methods involved in communicating with the
     * action queue.
     *
     * find:action-queue
     */
    setMatchView: function(matchView) {
        if (this.matchView) {
            this.matchView.off("queueAction");
            this.matchView.off("finishAction");
        }
        this.matchView = matchView;
        this.matchView.on("queueAction", this.queueAction, this);
        this.matchView.on("finishAction", this.finishAction, this);
    },
    queueAction: function(action) {
        if (action.get('winner')) {
            action.set('stage', SKAction.Stages.finished);
        } else if (action.get('finished_at')) {
            //TODO check that this works when finished At is done
            if (action.battle) {
                action.set("stage", SKAction.Stages.won);
            } else {
                action.set("stage", SKAction.Stages.finished);
            }
        } else {
            action.set('stage', SKAction.Stages.queued);
        }
        this.actions.push(action);
        this.render();
    },
    finishAction: function(action) {
        if (action.get('winner')) {
            action.set('stage', SKAction.Stages.finished);
        } else if (action.get('finished_at')) {
            //TODO check that this works when finished At is done
            if (action.battle) {
                action.set("stage", SKAction.Stages.won);
            } else {
                action.set("stage", SKAction.Stages.finished);
            }
        } else {
            if (action.battle) {
                action.set("stage", SKAction.Stages.ongoing);
            } else {
                action.set("stage", SKAction.Stages.finished);
            }
        }
        this.actions.push(action);
        this.render();
    }
});

SKUnitDefaultManager = {
    defaults: {},
    getDefaults: function(player) {
        return this.defaults[player.side] || [];
    },
    addDefault: function(type, player) {
        defaults = this.defaults[player.side]
        if (!defaults) {
            defaults = [];
            this.defaults[player.side] = defaults;
        }
        defaults.push({
            type: type,
            estimate: 0
        });
    },
    removeDefault: function(type, player) {
        for (var i=0, length=this.defaults[player.side].length; i<length; i++) {
            if (this.defaults[player.side][i].type == type) {
                this.defaults[player.side].splice(i,1);
                return;
            }
        }
    }
}

});
