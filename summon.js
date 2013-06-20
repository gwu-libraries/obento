// ==============================================
// Author:      Tito Sierra (tito_sierra@ncsu.edu)
// Created:     12/30/2009
// Description: Javascript and jQuery code to asynchronously request and display article search
//              results from the Summon API
// ==============================================

function stripslashes (str) {
    // +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +   improved by: Ates Goral (http://magnetiq.com)
    // +      fixed by: Mick@el
    // +   improved by: marrtins
    // +   bugfixed by: Onno Marsman
    // +   improved by: rezna
    // +   input by: Rick Waldron
    // +   reimplemented by: Brett Zamir (http://brett-zamir.me)
    // +   input by: Brant Messenger (http://www.brantmessenger.com/)
    // +   bugfixed by: Brett Zamir (http://brett-zamir.me)
    // *     example 1: stripslashes('Kevin\'s code');
    // *     returns 1: "Kevin's code"
    // *     example 2: stripslashes('Kevin\\\'s code');
    // *     returns 2: "Kevin\'s code"
    return (str + '').replace(/\\(.?)/g, function (s, n1) {
        switch (n1) {
        case '\\':
            return '\\';
        case '0':
            return '\u0000';
        case '':
            return '';
        default:
            return n1;
        }
    });
}

function get_article_items(totalArticleItems, items) {
  var seeAllArticlesLink = "http://ncsu.summon.serialssolutions.com/search?s.q=" + stripslashes(decodeURI(url_encoded_query)) + "&s.cmd=addFacetValueFilters%28ContentType%2CJournal+Article,Journal+%2F+eJournal,Book+Chapter%29 &keep_r=true";
  var itemsHtml = "<dl>\n";
  for (i = 0; i < items.length && i <= 2; i++) {
    var resultNumber = i + 1;
    //var itemArticleLink = "http://js8lb8ft5y.search.serialssolutions.com/?" + decodeURI(items[i]['openUrl']);
		var itemArticleLink = decodeURI(items[i]['link']);
    var itemArticleTitle = String(items[i]['Title']);
    
    var itemType = String(items[i]['ContentType']);
    itemType = itemType.replace(",", ", ");

    var itemFullText = String(items[i]['hasFullText']);

    itemArticleTitle = itemArticleTitle.replace(/<\/?[^>]+>/gi, '');
    if (itemArticleTitle.length > 85) {
      itemArticleTitle = itemArticleTitle.substring(0, 80) + "...";
    }
    
    itemsHtml += "<dt><a href=\"" + redirect_url + escape(itemArticleLink) + "&amp;q=" + url_encoded_query + "&amp;cat=FA&amp;ref=FA_RES_" + resultNumber + "\">"  + itemArticleTitle + "</a></dt>";
    
    var itemArticleAuthors = String(items[i]['Author']);
    if (itemArticleAuthors != "undefined") {
        if (itemArticleAuthors.length > 40) {
          itemArticleAuthors = itemArticleAuthors.substring(0, 38) + "...";
        }
      itemsHtml += "<dd>Author: " + itemArticleAuthors + "</dd>";
    }
    if (items[i]['PublicationTitle']) {
      itemsHtml += "<dd><span class=\"summonItemPublicationTitle\">" + items[i]['PublicationTitle'] + "</span>";
      if (items[i]['Volume']) {
        itemsHtml += ", V. " + items[i]['Volume'];
      }
      if (items[i]['PublicationDate_xml']) {
        itemsHtml += ", " + items[i]['PublicationDate_xml'][0]['year'];
      }
      itemsHtml += "</dd>"
    }
//     if (items[i]['Abstract']) {
//       var itemArticleAbstract = String(items[i]['Abstract']);
//       if (itemArticleAbstract.length > 140) {
//         itemArticleAbstract = itemArticleAbstract.substring(0, 136) + "...";
//       }
      // Excluding display of abstracts for now
      // itemsHtml += itemArticleAbstract;
    //}
    if (itemFullText === "true" && itemType.indexOf("Journal Article") !== -1) {
      itemsHtml += "<dd>" + itemType + "</dd>\n";
      itemsHtml += "<dd><img src=\"../website/images/pdf.gif\" height=\"14px\" width=\"14px\" alt=\"\"/> Full Text Online</dd>\n";
    } else {
      itemsHtml += "<dd>" + itemType + "</dd>\n";
    }
  }
  itemsHtml += "</dl>\n";
  itemsHtml += "<p class=\"seeAll\"><a  class=\"seeAll\" href=\"" + redirect_url + escape(seeAllArticlesLink) + "&amp;q=" + url_encoded_query + "&amp;cat=FA&amp;ref=FA_ALL\" id=\"summonSeeAllLink\"><span class='seeAllArrow'>&#8627;</span> See all " + addCommas(totalArticleItems)  + " articles from Summon</a></p>";
  $("#articleSearchResultsItems").html(itemsHtml);
}

$(function() {
  $.ajax( {
    url: "/search/includes/summon.php",
    data: "q=" + url_encoded_query,
    success: function(data) {
      if (searchpage != 'websearch.php') {
				$("#articleSearchResultsSpinner").hide();
				// Pull out data from javascript object
				var totalArticleItems = data['recordCount'];
				if (totalArticleItems > 0) {
					get_article_items(totalArticleItems, data['documents']);
				} else {
					$("#articleSearchResultsItems").html("<p><em>No article results found. Please try another search in <a href=\"" + redirect_url + escape("http://ncsu.summon.serialssolutions.com") + "&amp;q=" + url_encoded_query + "&amp;cat=FA&amp;ref=FA_NORESULTS\">Summon</a>.</em></p>");
				}
      }
      
      // Get Spelling Suggestion if any
      if (data.didYouMeanSuggestions[0]) {
      	var spellingSuggestion = data.didYouMeanSuggestions[0].suggestedQuery;
      }

      if (spellingSuggestion) {
				if (spellingSuggestion.length > 300) {
					spellingSuggestionDisplay = spellingSuggestion.substring(0, 290) + "...";
				} else {
					spellingSuggestionDisplay = spellingSuggestion;
				}
				
        if (searchpage != 'websearch.php') {
            var spellingHtml = "<div id='spellingWidget'><h2 class='spelling'>Did you mean: <a href='" + redirect_url +"/search/?q=" + escape(spellingSuggestion) + "&amp;q=" + url_encoded_query + "&amp;cat=SPELL'><span class='spelling'>" + spellingSuggestionDisplay + "</span></a></h2></div>";         
        } else {
            var spellingHtml = "<div id='spellingWidget'><h2 class='spelling'>Did you mean: <a href='" + redirect_url + "?target=/search/websearch.php?q=" + escape(spellingSuggestion) + "&amp;q=" + url_encoded_query + "&amp;service=websearch&amp;cat=SPELL'><span class='spelling'>" + spellingSuggestionDisplay + "</span></a></h2></div>";
         }
        $("#spelling").html(spellingHtml);
      }

    },
    error: function(data) {
        $("#articleSearchResultsSpinner").hide();
        $("#articleSearchResultsItems").html("<p><em>Service temporarily unavailable. Please redo your search in <a href=\"" + redirect_url + escape("http://ncsu.summon.serialssolutions.com") + "&amp;q=" + url_encoded_query + "&amp;cat=FA&amp;ref=FA_TIMEOUT\">Summon</a>.</em></p>");
    },
    timeout: 8000,
    dataType: "json"
  });
});
