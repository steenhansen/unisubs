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

goog.provide('unisubs.controls.VideoControls');
/**
* @constructor
* @extends goog.ui.Component
*/
unisubs.controls.VideoControls = function(videoPlayer) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
};
goog.inherits(unisubs.controls.VideoControls, goog.ui.Component);

unisubs.controls.VideoControls.prototype.createDom = function() {
    unisubs.controls.VideoControls.superClass_.createDom.call(this);
    this.getElement().className = 'unisubs-videoControls';
    this.addChild(new unisubs.controls.PlayPause(this.videoPlayer_), true);
    this.addChild(new unisubs.controls.ProgressBar(this.videoPlayer_), true);
    this.addChild(new unisubs.controls.TimeSpan(this.videoPlayer_), true);
    this.addChild(new unisubs.controls.VolumeControl(this.videoPlayer_), true);
};
