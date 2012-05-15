window.ESB = {};
Backbone.emulateJSON = true;

makeTestMatch = function() {
    var leftPlayer = new SKPlayer({race: 'protoss', name: 'Tony'})
    var rightPlayer = new SKPlayer({race: 'terran', name: 'Flo'})
    MatchView.match = new SKMatch(
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
    },
    getIconURL: function (unitName, mediaURL) {
        icon = unitName.toLowerCase().replace(new RegExp('[ -]', 'g'), '_');
        return mediaURL+"/sc2/icons/"+icon+".gif";
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
