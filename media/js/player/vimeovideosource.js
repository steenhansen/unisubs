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

goog.provide('unisubs.player.VimeoVideoSource');

/**
 * @constructor
 * @implements {unisubs.player.MediaSource}
 * @param {string} videoID Vimeo video id (unrelated to unisubs.player id)
 * @param {string} videoURL URL of Vimeo page
 * @param {Object.<string, *>=} opt_videoConfig Params to use for moogaloop player.
 */
unisubs.player.VimeoVideoSource = function(videoID, videoURL, opt_videoConfig) {
    this.videoID_ = videoID;
    this.videoURL_ = videoURL;
    this.uuid_ = unisubs.randomString();
    this.videoConfig_ = opt_videoConfig;
};

unisubs.player.VimeoVideoSource.prototype.createPlayer = function() {
    return this.createPlayer_(false);
};

unisubs.player.VimeoVideoSource.prototype.createControlledPlayer = function() {
    return new unisubs.player.ControlledVideoPlayer(this.createPlayer_(true));
};

unisubs.player.VimeoVideoSource.prototype.createPlayer_ = function(forDialog) {
    return new unisubs.player.VimeoVideoPlayer(
        new unisubs.player.VimeoVideoSource(
            this.videoID_, this.videoURL_, this.videoConfig_),
        forDialog);
};

unisubs.player.VimeoVideoSource.prototype.getVideoId = function() {
    return this.videoID_;
};

unisubs.player.VimeoVideoSource.prototype.getUUID = function() {
    return this.uuid_;
};

unisubs.player.VimeoVideoSource.prototype.getVideoConfig = function() {
    return this.videoConfig_;
};

unisubs.player.VimeoVideoSource.prototype.setVideoConfig = function(config) {
    this.videoConfig_ = config;
};

unisubs.player.VimeoVideoSource.prototype.getVideoURL = function() {
    return this.videoURL_;
};
/**
* Checks if this video url is indeed for this MediaSource type, returns a
* mediaSource subclass if it is, null if it isn't
*/
unisubs.player.VimeoVideoSource.getMediaSource = function(videoURL, opt_videoConfig) {
    if (/^\s*https?:\/\/([^\.]+\.)?vimeo/.test(videoURL)) {
        var videoIDExtract = /vimeo.com\/([0-9]+)/i.exec(videoURL);
        if (videoIDExtract)
            return new unisubs.player.VimeoVideoSource(
                videoIDExtract[1], videoURL, opt_videoConfig);
    }
    return null;
}

// add this mediaSource to our registry
unisubs.player.MediaSource.addMediaSource(unisubs.player.VimeoVideoSource.getMediaSource);
