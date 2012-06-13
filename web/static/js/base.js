window.ESB = {};
Backbone.emulateJSON = true;

ESB.Template = {
    make: function (id) {
        return _.template($('#'+id).html());
    }
};
ESB.Util = {
    stopPropagation: function(e) {
        var evt = e ? e:window.event;
        if (evt.stopPropagation)    evt.stopPropagation();
        if (evt.cancelBubble!=null) evt.cancelBubble = true;
    },
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
    },
    getIconURL: function (unitName, mediaURL) {
        icon = unitName.toLowerCase().replace(new RegExp('[ -]', 'g'), '_');
        return mediaURL+"/sc2/icons/"+icon+".gif";
    }
}
GAME_SPEED_MOD = .725
ESB.Timer = function(){
    this.time = 0;
    this.startTime = 0;
}
_.extend(ESB.Timer.prototype, Backbone.Events, {
    start: function() {
        this.startTime = new Date().getTime()/1000.0;
        window.setInterval(_.bind(this.tick, this), 1000*GAME_SPEED_MOD)
    },
    tick: function() {
        this.time = ((new Date().getTime()/1000) - this.startTime)/GAME_SPEED_MOD;
        this.trigger("tick", this)
    },
    displayClock: function() {
        return ESB.Timer.displayClock(this.time);
    }
});

ESB.Timer.displayClock = function(time){
    if (time!=null) {
        var minutes = Math.floor(time / 60);
        var seconds = Math.floor(time % 60);
        if (seconds < 10) {
            seconds = "0"+seconds;
        }
        if (minutes < 10) {
            minutes = "0"+minutes;
        }
        return "" + minutes + ":" + seconds;
    }
    return "";
};
