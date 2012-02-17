$(function() {

SKAction = Backbone.Model.extend({
    defaults: {
        stage: "inprogress",
        winner: null,
        winValue: 0,
    },
    initialize: function() {
        this.set("reinforcements_at", []);
        this.results = [];
    },
    addResult: function(result, index) {
        this.results.splice(index, 1, result); 
    },
    addReinforcements: function(time) {
        this.get("reinforcements_at").push(time);
    }
}); 

SKAction.createAction = function(id, side) {
//TODO add started to action
    var actions = SKAction.playerActions.concat(SKAction.nonPlayerActions);
    var i, length, action;
    for (i=0, length=actions.length; i < length; i++) {
        action = actions[i];
        if (action.id == id) {
            break;
        }
    }
    var actionOptions = {started_at: MatchTimer.time};
    if (side) {
        actionOptions.side = side;
    }
    actionOptions = $.extend(true, actionOptions, action);
    return new SKAction(actionOptions);
}

SKAction.Stages = {
    inprogress  : "inprogress", // Currently being worked on.
    reinforcing : "reinforcing",// Has been worked on but the reinforcements are being added.
    queued      : "queued",     // Queued, but not complete.
    ongoing     : "ongoing",    // Some actions are ongoing like engagements.
    won         : "won",        // Game is won, but the winner has not been set.
    finished    : "finished",   // Completely done no more info needed. can revert to inprogress.
    hidden      : "hidden"      // No longer showing up in the queue.
}

SKAction.playerActions = [
    //{name: "Base Built", id: 1, battle: false},
    //{name: "Base Destroyed", id:2, battle: false},
    {name: "Base Invaded", id:3, battle: true},
    {name: "Harassment", id:4, battle: true},
    //{name: "Macro", id:5, battle: false}
];
SKAction.nonPlayerActions = [
    {name:"Engagement", id:6, battle: true}
];

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
        this.leftPlayer = this.options.left;
        this.rightPlayer = this.options.right;
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
        for (i=0, length=this.action.results.length; i < length; i++) {
            pane = this.panes[i];
            result = this.action.results[i];
            pane.setResult(result);
        }
        this.paneIndex = Math.min(this.action.results.length, this.panes.length-1);
    },
    destroy: function() {
        this.undelegateEvents();
    }
});

SKActionView.createActionView = function(options) {
    var side = options.action.get('side');
    options.actor = options[side];
    options.receiver = options[side=="left"?"right":"left"];
    switch (options.action.get('id')) {
        case 1:
            return new SKActionBaseBuilt(options);
        case 2:
            return new SKActionBaseDestroyed(options);
        case 3:
            return new SKActionBaseInvaded(options);
        case 4:
            return new SKActionHarassment(options);
        case 5:
            return new SKActionMacro(options);
        case 6:
            return new SKActionEngagement(options);
    }
}

/* Actions */

/*
 * Unused currently
SKActionBaseBuilt = SKActionView.extend({
    buildPanes: function() {
        this.panes = []
    }
});
SKActionBaseDestroyed = SKActionView.extend({
    buildPanes: function() {
        this.panes = []
    }
});
*/
SKActionBaseInvaded = SKActionView.extend({
    buildPanes: function() {
        this.panes = [
            new SKPaneUnitComposition({
                title: this.actor.name + "'s Army",
                armory: {
                    units: SKArmoryView.Units[this.actor.race]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.name + "'s Defenses",
                armory: {
                    units: SKArmoryView.Units[this.receiver.race],
                    structures: SKArmoryView.Units[this.receiver.structures]
                }
            })
        ];
    },
    createReinforcementPanes: function() {
        return [
            new SKPaneUnitComposition({
                title: this.actor.name + "'s Reinforcements",
                armory: {
                    units: SKArmoryView.Units[this.actor.race]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.name + "'s Reinforcements",
                armory: {
                    units: SKArmoryView.Units[this.receiver.race],
                    structures: SKArmoryView.Units[this.receiver.structures]
                }
            })
        ];
    }
});
SKActionHarassment = SKActionView.extend({
    buildPanes: function() {
        this.panes = [
            new SKPaneUnitComposition({
                title: this.actor.name + "'s Harassment",
                armory: {
                    units: SKArmoryView.Units[this.actor.race]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.name + "'s Defenses",
                armory: {
                    units: SKArmoryView.Units[this.receiver.race],
                    structures: SKArmoryView.Units[this.receiver.structures]
                }
            })
        ];
    },
    createReinforcementPanes: function() {
        return [
            new SKPaneUnitComposition({
                title: this.actor.name + "'s Reinforcements",
                armory: {
                    units: SKArmoryView.Units[this.actor.race]
                }
            }),
            new SKPaneUnitComposition({
                title: this.receiver.name + "'s Reinforcements",
                armory: {
                    units: SKArmoryView.Units[this.receiver.race],
                    structures: SKArmoryView.Units[this.receiver.structures]
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
                title: this.leftPlayer.name + "'s Army",
                armory: {
                    units: SKArmoryView.Units[this.leftPlayer.race]
                }
            }),
            new SKPaneUnitComposition({
                title: this.rightPlayer.name + "'s Army",
                armory: {
                    units: SKArmoryView.Units[this.rightPlayer.race]
                }
            })
        ];
    },
    createReinforcementPanes: function() {
        return [
            new SKPaneUnitComposition({
                title: this.leftPlayer.name + "'s Reinforcements",
                armory: {
                    units: SKArmoryView.Units[this.leftPlayer.race]
                }
            }),
            new SKPaneUnitComposition({
                title: this.rightPlayer.name + "'s Reinforcements",
                armory: {
                    units: SKArmoryView.Units[this.rightPlayer.race]
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
    addQuantity: function(element) {
        var sameQuantity;
        var i, length, quantity;
        for (i=0, length=this.quantities.length; i < length; i++) {
            quantity = this.quantities[i]
            if (quantity.type == element) {
                sameQuantity=quantity;
            }
        }
        if (sameQuantity) {
            //TODO scroll to element if its not visible
            sameQuantity.shake();
        } else {
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
        var i, length, result, quantity;
        for (i=0, length=resultList.length; i<length; i++) {
            result = resultList[i];
            quantity = this.createQuantity(result.type);
            quantity.estimate = result.estimate;
        }
    }
});

SKActionQueueView = Backbone.View.extend({
    tmpl: ESB.Template.make('SKActionQueueView'),
    initialize: function() {
        this.actions = [];
    },
    events: {
        'click .queue-action .btn': "advanceStage"
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
    getActionOptions: function(action) {
        switch(action.get('stage')) {
            case "queued":
                return {
                    buttons: [{stage: SKAction.Stages.inprogress, text: "Work On"}],
                    statusText: "Queued...",
                    action: action
                }
            case "ongoing":
                var finishAction;
                if (action.get("battle")) {
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
            case "won":
                return {
                    statusText: "Finshed...",
                    action: action
                }
            case "finished":
                return {
                    buttons: [
                        {stage: SKAction.Stages.inprogress, text: "Work On"},
                        {stage: SKAction.Stages.hidden, text: "Hide"}
                    ],
                    statusText: "Finished...",
                    action: action
                }
        }
    },
    advanceStage: function(evt) {
        var button = $(evt.target);
        var stage = button.data('stage');
        var index = button.data('action-index');
        var action = this.actions[index];
        action.set("stage", stage);
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
                if (action.get('battle')) {
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
                    action.set("win_value", winValue)
                    action.set("winner", winner);
                }
            case SKAction.Stages.won:
                action.set("finished_at", MatchTimer.time);
                break;
            case SKAction.Stages.hidden:
                this.actions.splice(index, 1);
                break;
            default:
        }
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
            if (action.get("battle")) {
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
            if (action.get("battle")) {
                action.set("stage", SKAction.Stages.won);
            } else {
                action.set("stage", SKAction.Stages.finished);
            }
        } else {
            if (action.get("battle")) {
                action.set("stage", SKAction.Stages.ongoing);
            } else {
                action.set("stage", SKAction.Stages.finished);
            }
        }
        this.actions.push(action);
        this.render();
    }
});

});
