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

goog.provide('unisubs.player.WistiaVideoSource');

//unisubs.player.WistiaVideoSource = function(wistiaVideoURL) {  };

/**
 * @constructor
 * @implements {unisubs.player.MediaSource}
 * @param {string} videoID Vimeo video id (unrelated to unisubs.player id)
 * @param {string} videoURL URL of Vimeo page
 * @param {Object.<string, *>=} opt_videoConfig Params to use for moogaloop player.
 */
unisubs.player.WistiaVideoSource = function(videoID, videoURL, opt_videoConfig) {
    this.videoID_ = videoID;
    this.videoURL_ = videoURL;
    this.uuid_ = unisubs.randomString();
    this.videoConfig_ = opt_videoConfig;
};

unisubs.player.WistiaVideoSource.prototype.createPlayer = function() {
    return this.createPlayer_(false);
};

unisubs.player.WistiaVideoSource.prototype.createControlledPlayer = function() {
    return new unisubs.player.ControlledVideoPlayer(this.createPlayer_(true));
};

unisubs.player.WistiaVideoSource.prototype.createPlayer_ = function(forDialog) {
    return new unisubs.player.WistiaVideoPlayer(
        new unisubs.player.WistiaVideoSource(
            this.videoID_, this.videoURL_, this.videoConfig_),
        forDialog);
};

unisubs.player.WistiaVideoSource.prototype.getVideoId = function() {
    return this.videoID_;
};

unisubs.player.WistiaVideoSource.prototype.getUUID = function() {
    return this.uuid_;
};

unisubs.player.WistiaVideoSource.prototype.getVideoConfig = function() {
    return this.videoConfig_;
};

unisubs.player.WistiaVideoSource.prototype.setVideoConfig = function(config) {
    this.videoConfig_ = config;
};

unisubs.player.WistiaVideoSource.prototype.getVideoURL = function() {
    return this.videoURL_;
};

unisubs.player.WistiaVideoSource.getMediaSource = function(videoURL, opt_videoConfig) {
    // from http://wistia.com/doc/oembed
    // long regex /https?:\/\/(.+)?(wistia\.com|wi\.st)\/(medias|embed)\/.*/
    // short future safe regex /https?:\/\/(.+)?(wistia\.com|wi\.st)\/.*/
    // example http://home.wistia.com/medias/e4a27b971d
    // example http://fast.wistia.com/embed/iframe/b0767e8ebb?version=v1&controlsVisibleOnLoad=true&playerColor=aae3d8
 
  //           http://hootsuite.wistia.com/medias/17bvist1ia
    
    if (/^\s*https?:\/\/(.+)?(hootsuite\.wistia\.com|wi\.st)\/(medias|embed)\/.*/.test(videoURL)) {
      var videoIDExtract = /(hootsuite\.wistia\.com|wi\.st)\/(medias|embed)\/(iframe\/)?([^\?]*)/i.exec(videoURL);
      console.log(videoIDExtract);
      if (videoIDExtract)
        return new unisubs.player.WistiaVideoSource(videoIDExtract[4], videoURL, opt_videoConfig);
    }
    return null;
}

// add this mediaSource to our registry
unisubs.player.MediaSource.addMediaSource(unisubs.player.WistiaVideoSource.getMediaSource);
