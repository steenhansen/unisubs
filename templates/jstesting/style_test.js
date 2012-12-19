{% extends "jstesting/base_test.html" %}

{% block testscript %}
var testElem;

function setUp() {
    testElem = document.createElement('div');
}

function makeStyleArray(value) {
    return goog.array.filter(
        goog.array.map(
            value.split(';'),
            function(s) { return s.toLowerCase(); }),
        function(s) { return s.length > 0; });
}

function assertStyleEquals(expected, actual) {
    var expectedSet = new goog.structs.Set(makeStyleArray(expected));
    var actualArray = makeStyleArray(actual);
    assertEquals(expectedSet.getCount(), actualArray.length);
    for (var i = 0; i < actualArray.length; i++)
        assertTrue(expectedSet.contains(actualArray[i]));
}

function testSetSize() {
    unisubs.style.setSize(testElem, 32, 58);
    assertStyleEquals(
        "width:32px!important;height:58px!important;",
        testElem.style.cssText.replace(/ /gi, ''));
    unisubs.style.setWidth(testElem, 33);
    assertStyleEquals("width:33px!important;height:58px!important;",
                 testElem.style.cssText.replace(/ /gi, ''));
    unisubs.style.setHeight(testElem, 59);
    assertStyleEquals("width:33px!important;height:59px!important;",
                 testElem.style.cssText.replace(/ /gi, ''));
}

function testSetPosition() {
    unisubs.style.setPosition(testElem, new goog.math.Coordinate(32, 58));
    assertStyleEquals("left:32px!important;top:58px!important;",
                 testElem.style.cssText.replace(/ /g, ''));
    unisubs.style.setPosition(testElem, null, 59);
    assertStyleEquals("left:32px!important;top:59px!important;",
                 testElem.style.cssText.replace(/ /g, ''));
    unisubs.style.setPosition(testElem, 33, null);
    assertStyleEquals("left:33px!important;top:59px!important;",
                 testElem.style.cssText.replace(/ /g, ''));
    unisubs.style.setPosition(testElem, new goog.math.Coordinate(34, 60));
    assertStyleEquals("left:34px!important;top:60px!important;",
                 testElem.style.cssText.replace(/ /g, ''));
}

function testShow() {
    unisubs.style.showElement(testElem, false);
    assertStyleEquals('display:none!important;',
                 testElem.style.cssText.replace(/ /g, ''));
    unisubs.style.showElement(testElem, true);
    assertEquals('', testElem.style.cssText);
}

function testSetVisibility() {
    unisubs.style.setVisibility(testElem, false);
    assertStyleEquals('visibility:hidden!important;',
                 testElem.style.cssText.replace(/ /g, ''));
    unisubs.style.setVisibility(testElem, true);
    assertStyleEquals('visibility:visible!important;',
                 testElem.style.cssText.replace(/ /g, ''));
}

function testSetImportant() {
    testElem.style.top = "15px";
    testElem.style.left = "20px";
    unisubs.style.setProperty(testElem, "width", "80px");
    unisubs.style.makeStylesImportant(testElem);
    assertStyleEquals("left:20px!important;top:15px!important;width:80px!important",
                 testElem.style.cssText.replace(/ /g, ''));
}

{% endblock %}