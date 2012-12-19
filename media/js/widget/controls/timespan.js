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

goog.provide('unisubs.controls.TimeSpan');

/**
* @constructor
* @extends goog.ui.Component
*/
unisubs.controls.TimeSpan = function(videoPlayer) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
    this.currentlyDisplayedSecond_ = -1;
    this.durationSet_ = false;
};
goog.inherits(unisubs.controls.TimeSpan, goog.ui.Component);
unisubs.controls.TimeSpan.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.timeElapsedLabel_ = $d('div', 'unisubs-timeElapsed');
    this.totalTimeLabel_ = $d('span');
    this.setElementInternal(
        $d('span', 'unisubs-timespan',
           this.timeElapsedLabel_, this.totalTimeLabel_));
};
unisubs.controls.TimeSpan.prototype.enterDocument = function() {
    unisubs.controls.TimeSpan.superClass_.enterDocument.call(this);
    // TODO: alternative here is to set a 1-second interval timer and
    // query playheadTime on each tick. Decide if that has better
    // performance.
    this.getHandler().listen(
        this.videoPlayer_,
        unisubs.player.AbstractVideoPlayer.EventType.TIMEUPDATE,
        this.videoTimeUpdate_);
};
unisubs.controls.TimeSpan.prototype.videoTimeUpdate_ = function() {
    if (~~this.videoPlayer_.getPlayheadTime() != this.currentlyDisplayedSecond_) {
        if (!this.durationSet_) {
            var duration = this.videoPlayer_.getDuration();
            if (duration == 0)
                return;
            goog.dom.setTextContent(this.totalTimeLabel_,
                                    '/' + unisubs.formatTime(duration * 1000, true));
            this.durationSet_ = true;
        }
        var playheadSecs = ~~this.videoPlayer_.getPlayheadTime();
        this.currentlyDisplayedSecond_ = playheadSecs;
        goog.dom.setTextContent(
            this.timeElapsedLabel_,
            unisubs.formatTime(playheadSecs * 1000, true));
    }
};
