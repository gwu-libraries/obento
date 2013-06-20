// This function adds commas to numbers to group digits by 3
// Borrowed from http://www.mredkj.com/javascript/nfbasic.html
function addCommas(nStr)
{
	nStr += '';
	x = nStr.split('.');
	x1 = x[0];
	x2 = x.length > 1 ? '.' + x[1] : '';
	var rgx = /(\d+)(\d{3})/;
	while (rgx.test(x1)) {
		x1 = x1.replace(rgx, '$1' + ',' + '$2');
	}
	return x1 + x2;
}

$(document).ready(function() {
	var numberOfResults = $('span.hitCount').text();
	numberOfResults = addCommas(numberOfResults);
	$('span.hitCount').replaceWith(numberOfResults);
});