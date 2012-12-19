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

if (!window['{{gatekeeper}}']) {
    var d = document, w = window;
    function addScript() {
        var script = d.createElement('script');
        script.src = "{{script_src}}";
        script.async = true;
        var firstScript = d.getElementsByTagName('script')[0];
        firstScript.parentNode.insertBefore(script, firstScript);
    };

    var readyArrayName = "unisubsReady";
    var readyArray = w[readyArrayName] = w[readyArrayName] || [];

    var readyFuncName = "unisubsPlayerReady";
    w[readyFuncName] = function(code, args) {
        readyArray.push([code, args]);
    };

    function addReadyListener(callback, code) {
        var oldReady = w[callback] || function() {};
        w[callback] = function() {
            try {
                oldReady.apply(null, arguments);
            }
            catch (e) {
                // don't care
            }
            w[readyFuncName](code, arguments);
        };
    }

    addReadyListener("onYouTubePlayerReady", "y");
    addReadyListener("us_ooyala_callback", "o");
    addReadyListener("onTemplateLoaded", "b");

    if (d.readyState == "complete") {
        addScript();
    }
    else {
        if (w.addEventListener) {
            w.addEventListener("load", addScript, false);
        }
        else {
            w.attachEvent("onload", addScript);
        }
    }
}
