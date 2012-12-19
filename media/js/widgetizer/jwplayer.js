// Amara, universalsubtitles.org
// 
// Copyright (C) 2012 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('unisubs.widgetizer.JWPlayer');

/**
 * @constructor
 *
 */
unisubs.widgetizer.JWPlayer = function() {
    unisubs.widgetizer.VideoPlayerMaker.call(this);
    this.VIDS_ARE_JW_ =
        window.location.hostname.match(/ocw\.mit\.edu/) != null ||
        window['UNISUBS_JW_ONLY'];
};
goog.inherits(
    unisubs.widgetizer.JWPlayer,
    unisubs.widgetizer.VideoPlayerMaker);

unisubs.widgetizer.JWPlayer.prototype.makeVideoPlayers = function() {
    var elements = this.unwidgetizedElements_();
    var videoPlayers = [];
    for (var i = 0; i < elements.length; i++) {
        var videoSource = this.makeVideoSource_(elements[i]);
        var videoPlayer = new unisubs.player.JWVideoPlayer(videoSource);
        videoPlayers.push(videoPlayer);
        videoPlayer.decorate(elements[i]);
    }
    return videoPlayers;
};

unisubs.widgetizer.JWPlayer.prototype.makeVideoSource_ = function(elem) {
    var matches = /file=([^&]+)/.exec(unisubs.Flash.flashVars(elem));
    return unisubs.player.YoutubeVideoSource.forURL(matches[1]);
};

unisubs.widgetizer.JWPlayer.prototype.unwidgetizedElements_ = function() {
    return unisubs.widgetizer.JWPlayer.superClass_.
        unwidgetizedFlashElements.call(this);
};

unisubs.widgetizer.JWPlayer.prototype.isFlashElementAPlayer = function(element) {    
    var swfSrc = unisubs.Flash.swfURL(element);
    var isJW = this.VIDS_ARE_JW_ && swfSrc.match(/player[^\.]*.swf$/i) != null;
    return isJW;
};
