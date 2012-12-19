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

goog.provide('unisubs.LoadingDom');

/**
 * @constructor
 * This is a singleton, so use unisubs.LoadingDom.getInstance() instead.
 */
unisubs.LoadingDom = function() {
    goog.events.EventTarget.call(this);
    this.isDomLoaded_ = false;
    var that = this;
    if (document.addEventListener) {
        var EVENT = "DOMContentLoaded";
        document.addEventListener(
            EVENT,
            function() {
                document.removeEventListener(EVENT, arguments.callee, false);
                that.onDomLoaded_();
            }, false);
    }
    else if (document.attachEvent) {
        this.listenOnIE_();
    }
    // in case nothing else works: load event
    goog.events.listenOnce(
        window, goog.events.EventType.LOAD,
        this.onDomLoaded_, false, this);
};
goog.inherits(unisubs.LoadingDom, goog.events.EventTarget);
goog.addSingletonGetter(unisubs.LoadingDom);

unisubs.LoadingDom.DOMLOAD = 'domloaded';

unisubs.LoadingDom.prototype.listenOnIE_ = function() {
    var that = this;
    var EVENT = "onreadystatechange";
    document.attachEvent(EVENT, function() {
        if (document.readyState == "complete") {
            document.detachEvent(EVENT, arguments.callee);
            that.onDomLoaded_();
        }
    });
    if (document.documentElement.doScroll && window == window.top)
        (function() {
            if (that.isDomLoaded_)
                return;
            try {
                // Thanks to Diego Perini: http://javascript.nwbox.com/IEContentLoaded/
                document.documentElement.doScroll('left');
            }
            catch (error) {
                setTimeout(arguments.callee, 0);
                return;
            }
            that.onDomLoaded_();
        })();
};

unisubs.LoadingDom.prototype.onDomLoaded_ = function() {
    if (this.isDomLoaded_)
        return;
    this.isDomLoaded_ = true;
    this.dispatchEvent(unisubs.LoadingDom.DOMLOAD);
};

unisubs.LoadingDom.prototype.isDomLoaded = function() {
    return this.isDomLoaded_ || document.readyState == 'complete';
};
