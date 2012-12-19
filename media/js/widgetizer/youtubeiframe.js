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

goog.provide('unisubs.widgetizer.YoutubeIFrame');

/**
 * @constructor
 *
 */
unisubs.widgetizer.YoutubeIFrame = function() {
    unisubs.widgetizer.VideoPlayerMaker.call(this);
};
goog.inherits(unisubs.widgetizer.YoutubeIFrame,
              unisubs.widgetizer.VideoPlayerMaker);

unisubs.widgetizer.YoutubeIFrame.prototype.makeVideoPlayers = function() {
    var iframes = this.unwidgetizedIFrames_();
    var videoPlayers = [];
    goog.array.forEach(
        iframes,
        function(iframe) {
            var decoratable = this.isDecoratable_(iframe);
            var videoSource = this.makeVideoSource_(iframe, !decoratable);
            var videoPlayer = videoSource.createPlayer();
            videoPlayers.push(videoPlayer);
            if (decoratable)
                videoPlayer.decorate(iframe);
            else
                this.replaceIFrameElement_(videoPlayer, iframe);
        }, 
        this);
    return videoPlayers;
};

unisubs.widgetizer.YoutubeIFrame.prototype.isDecoratable_ = function(iframe) {
    var uri = new goog.Uri(iframe['src'], true);
    return uri.getParameterValue('enablejsapi') == '1' &&
        goog.array.contains(['transparent', 'opaque'], 
                            uri.getParameterValue('wmode')) &&
        !!uri.getParameterValue('origin');
};

unisubs.widgetizer.YoutubeIFrame.prototype.makeVideoSource_ = function(iframe, includeConfig) {
    var url = iframe['src'];
    var config = null;
    if (includeConfig) {
        config = {};
        var uri = new goog.Uri(url, true);
        var params = uri.getQueryData().getKeys();
        for (var i = 0; i < params.length; i++)
            config[params[i]] = uri.getParameterValue(params[i]);
        config['width'] = iframe['width'];
        config['height'] = iframe['height'];
    }
    return unisubs.player.YTIFrameVideoSource.forURL(url, config);
};

unisubs.widgetizer.YoutubeIFrame.prototype.replaceIFrameElement_ = function(player, element) {
    // FIXME: some duplication with Youtube#replaceVideoElement_
    var nextNode = goog.dom.getNextElementSibling(element);
    var parent = element.parentNode;
    goog.dom.removeNode(element);
    if (nextNode)
        player.renderBefore(nextNode);
    else
        player.render(parent);
};

unisubs.widgetizer.YoutubeIFrame.prototype.unwidgetizedIFrames_ = function() {
    var iframes = goog.dom.getElementsByTagNameAndClass('iframe');
    var youtubeIFrames = goog.array.filter(
        iframes,
        function(iframe) { 
            return unisubs.player.YoutubeVideoSource.isYoutube(iframe['src']); 
        });
    return this.filterUnwidgetized(youtubeIFrames);
};
