$(function() {

SKArmoryQuantityView = Backbone.View.extend({
    tmpl: ESB.Template.make('SKArmoryQuantityView'),
    events: {
        'click .quantity-estimate'  : 'estimateQuantity',
        'click .quantity-adjuster'  : 'adjustQuantity',
        'click .remove'             : 'signalRemove',
        'change .quantity'          : 'setQuantity',
        'click .quantity'           : 'clearQuantity'
    },
    initialize: function () {
        this.amount = 0;
        this.type = this.options.type
    },
    render: function() {
        var options = {
            type: this.type,
            selectedEstimate: this.estimate,
            estimates: ["<30", "20", "10", "5", "4", "3", "2", "1"],
            amount: this.amount,
        }
        $(this.el).html(
            this.tmpl(options)
        );
        this.delegateEvents();
        return $(this.el);
    },
    estimateQuantity: function(evt) {
        var estimate = $(evt.target).attr('data-estimate');
        console.log(estimate)
        if (estimate == this.estimate) {
            this.estimate = null;
        } else {
            this.estimate = estimate;
        }
        this.render();
    },
    adjustQuantity: function(evt) {
        if ($(evt.target).data('adjust')=="up") {
            this.amount++;
        } else {
            this.amount--;
        }
        this.estimate=null;
        this.render();
    },
    setQuantity: function() {
        this.amount = parseInt(this.$(".quantity").val());
    },
    clearQuantity: function() {
        this.$(".quantity").val('');
    },
    signalRemove: function() {
        this.trigger('remove', this);
    },
    shake: function() {
        $(this.el).css({position: 'relative'});
        $(this.el).animate({left:'-5px'}, 100)
            .animate({left:'5px'}, 100)
            .animate({left:'-5px'}, 100)
            .animate({left:'5px'}, 100)
            .animate({left:'0px'}, 50)
    }
});

SKArmoryView = Backbone.View.extend({
    tmpl: ESB.Template.make('SKArmoryView'),
    resultsTmpl: ESB.Template.make('SKArmoryViewResults'),
    events: {
        'keyup .armory-search'          : 'handleKey',
        'click .armory-search-result'   : 'clickedElement',
        'click .armory-icon'            : 'clickedElement'
    },
    render: function() {
        var options = {
            results: this.results || [],
            resultIndex: this.resultIndex,
            elements: {
                units: this.units,
                structures: this.structures,
                upgrades: this.upgrades
            }
        };
        $(this.el).html(
            this.tmpl(options)
        );
        this.renderResults();
        return $(this.el);
    },
    renderResults: function() {
        var options = {
            results: this.results || [],
            resultIndex: this.resultIndex
        };
        this.$('.armory-search-results').html(
            this.resultsTmpl(options)
        );
        if (!this.results || this.results.length==0) {
            this.$(".armory-search-results").hide();
        } else { 
            this.$(".armory-search-results").show();
        }
    },
    initialize: function() {
        this.units =  this.options.units;
        this.structures =  this.options.structures;
        this.upgrades =  this.options.upgrades;
    },
    handleKey: function(evt) {
        switch(evt.which) {
        case 38:
            this.resultIndex = Math.max(this.resultIndex-1, 0);
            this.renderResults();
            break;
        case 40:
            this.resultIndex = Math.min(this.resultIndex+1, this.results.length-1);
            this.renderResults();
            break;
        case 13:
            if (this.results && this.results.length) {
                this.chooseElement(this.results[this.resultIndex])
            }
            break;
        default:
            this.showResults();
        }
    },
    showResults: function() {
        var query = this.$('.armory-search').val();
        var results = [];
        if (query.length) {
            var elements = (this.units || []).concat(this.structures || []).concat(this.upgrades || []);
            var words;
            var element;
            var word;
            for (var i=0, length=elements.length; i < length; i++) {
                element = elements[i];
                words = element.split(RegExp('[ -]'));
                for (var j=0, wLength=words.length; j < wLength; j++) {
                    word = words[j];
                    if (word.toLowerCase().indexOf(query.toLowerCase())==0) {
                        results.push(element)
                        break;
                    }
                }
            }
        }
        this.results = results;
        this.resultIndex = 0;
        this.renderResults();
    },
    clickedElement: function(evt) {
        var element = $(evt.target).data('name');
        this.chooseElement(element);
    },
    chooseElement: function(element) {
        this.trigger('elementSelected', element);
    }
});

SKArmoryView.Units = {
    terran: [
        'SCV',
        'MULE',
        'Marine',
        'Marauder',
        'Reaper',
        'Ghost',
        'Hellion',
        'Siege Tank',
        'Thor',
        'Viking',
        'Medivac',
        'Raven',
        'Banshee',
        'Battlecruiser',
        'Auto-Turret',
        'Point Defense Drone'
    ],
    protoss: [
        'Probe',
        'Zealot',
        'Stalker',
        'Sentry',
        'Observer',
        'Immortal',
        'Warp Prism',
        'Colossus',
        'Phoenix',
        'Void Ray',
        'High Templar',
        'Dark Templar',
        'Archon',
        'Carrier',
        'Interceptor',
        'Mothership'
    ],
    zerg: [
        'Larva',
        'Drone',
        'Overlord',
        'Zergling',
        'Queen',
        'Hydralisk',
        'Baneling',
        'Overseer',
        'Roach',
        'Infestor',
        'Infested Terran',
        'Mutalisk',
        'Corruptor',
        'Nydus Worm',
        'Ultralisk',
        'Brood Lord',
        'Broodling',
        'Changeling'
    ]
}
SKArmoryView.Structures = {
    terran: [
        'Command Center',
        'Supply Depot',
        'Refinery',
        'Barracks',
        'Orbital Command',
        'Planetary Fortress',
        'Engineering Bay',
        'Bunker',
        'Missile Turret',
        'Sensor Tower',
        'Factory',
        'Ghost Academy',
        'Armory',
        'Starport',
        'Fusion Core',
        'Tech Lab',
        'Reactor'
    ],
    protoss: [
        'Nexus',
        'Pylon',
        'Assimilator',
        'Gateway',
        'Forge',
        'Photon Cannon',
        'Warp Gate',
        'Cybernetics Core',
        'Twilight Council',
        'Robotics Facility',
        'Stargate',
        'Templar Archives',
        'Dark Shrine',
        'Robotics Bay',
        'Fleet Beacon'
    ],
    zerg: [
        'Hatchery',
        'Extractor',
        'Spawning Pool',
        'Evolution Chamber',
        'Spine Crawler',
        'Spore Crawler',
        'Hydralisk Den',
        'Baneling Nest',
        'Lair',
        'Roach Warren',
        'Infestation Pit',
        'Spire',
        'Nydus Network',
        'Hive',
        'Ultralisk Cavern',
        'Greater Spire',
        'Creep Tumor'
    ]
}
SKArmoryView.Upgrades = {
    terran: [
        '250mm Strike Cannons',
        'Behemoth Reactor',
        'Caduceus Reactor',
        'Cloaking Field',
        'Combat Shield',
        'Concussive Shells',
        'Corvid Reactor',
        'Durable Materials',
        'Hi-Sec Auto Tracking',
        'Infernal Pre-igniter',
        'Moebius Reactor',
        'Neosteel Frame',
        'Nitro Packs',
        'Personal Cloaking',
        'Seeker Missile',
        'Siege Tech',
        'Stimpack',
        'Building Armor',
        'Infantry Armor 1',
        'Infantry Armor 2',
        'Infantry Armor 3',
        'Infantry Weapons 1',
        'Infantry Weapons 2',
        'Infantry Weapons 3',
        'Ship Plating 1',
        'Ship Plating 2',
        'Ship Plating 3',
        'Ship Weapons 1',
        'Ship Weapons 2',
        'Ship Weapons 3',
        'Vehicle Plating 1',
        'Vehicle Plating 2',
        'Vehicle Plating 3',
        'Vehicle Weapons 1',
        'Vehicle Weapons 2',
        'Vehicle Weapons 3',
        'Weapon Refit'
    ],
    protoss: [
        'Blink',
        'Charge',
        'Extended Thermal Lance',
        'Gravitic Boosters',
        'Gravitic Drive',
        'Graviton Catapult',
        'Hallucination',
        'Air Armor 1',
        'Air Armor 2',
        'Air Armor 3',
        'Air Weapons 1',
        'Air Weapons 2',
        'Air Weapons 3',
        'Ground Armor 1',
        'Ground Armor 2',
        'Ground Armor 3',
        'Ground Weapons 1',
        'Ground Weapons 2',
        'Ground Weapons 3',
        'Shields 1',
        'Shields 2',
        'Shields 3',
        'Psionic Storm',
        'Warp Gate Upgrade'
    ],
    zerg: [
        'Adrenal Glands',
        'Burrow',
        'Centrifugal Hooks',
        'Chitinous Plating',
        'Glial Reconstitution',
        'Grooved Spines',
        'Metabolic Boost',
        'Neural Parasite',
        'Pathogen Glands',
        'Pneumatized Carapace',
        'Tunneling Claws',
        'Ventral Sacs',
        'Flyer Attacks 1',
        'Flyer Attacks 2',
        'Flyer Attacks 3',
        'Flyer Carapace 1',
        'Flyer Carapace 2',
        'Flyer Carapace 3',
        'Ground Carapace 1',
        'Ground Carapace 2',
        'Ground Carapace 3',
        'Melee Attacks 1',
        'Melee Attacks 2',
        'Melee Attacks 3',
        'Missile Attacks 1',
        'Missile Attacks 2',
        'Missile Attacks 3'
    ]
}
});
