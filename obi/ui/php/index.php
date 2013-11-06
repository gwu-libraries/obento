<!doctype html>
<html>
    <head>
        <meta charset='utf-8' />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GW Libraries Search: PUT TITLE HERE</title>

        <script type='text/javascript' src='//code.jquery.com/jquery-1.10.2.min.js' />
        <script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/js/bootstrap.min.js"></script>

        <!-- feedback form -->
        <script type='text/javascript'>
        function formFeedback() {
            var formUrl = "https://docs.google.com/forms/d/1YNODxi35XiJEv80wOJDFV3H2IIfOYmU3K5hCU8SfunE/viewform?entry.229836285=" + encodeURIComponent(location.href);
                window.open(formUrl);
        }
        </script>

	<script type='text/javascript'>
        $.urlParam = function(name){
            var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
            return results[1] || 0;
        }
	$(document).ready(function() {
            var data = $.urlParam('query');
	    var bento_url = "http://gwdev-kerchner.wrlc.org:8080/";

	    function fetch(vals) {
		$.post('obento/proxyscript.php',
            {"url": bento_url+vals[0]+"?q="+data+"&remote_addr="+"<?php echo $_SERVER["REMOTE_ADDR"] ?>"},
			function(response){
       	           		$(vals[1]).html(response);
			}
		);
    	    };

	    var blocks = [
        	["best_bets_html", '#bestbets-response'],
		["articles_html", '#articles-response'],
		["databases_solr_html", '#databases-solr-response'],
		["books_media_html", '#books-response'],
		["journals_solr_html", '#journals-solr-response'],
		["libsite_html", '#libsite-response'],
		["research_guides_html", '#guides-response'],
	    ];
	    blocks.forEach(fetch);
	});
	</script>

    </head>
    <body>

<?php if ($_GET["query"])
{
?>
<div id='results' class='row-fluid'>
    <div id='bestbets-articles-databases' class='span4'>
        <div id='bestbets-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <h4>Articles</h4>
        <div id='articles-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr />
        <h4>Databases</h4>
        <div id='databases-solr-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
    </div>
    <div id='books-journals' class='span4 left-border'>
        <h4>Books &amp; Media</h4>
        <div id='books-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr />
        <h4 class='separate-top'>Journals</h4>
        <div id='journals-solr-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
    </div>
    <div id='website-other' class='span4 left-border'>
        <h4>Library Website</h4>
        <div id='libsite-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr />
        <h4>Research Guides</h4>
        <div id='guides-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
    </div>
</div>
<?php
}
?>

        <div class='container'>
            <div class='row-fluid'>
                <hr />
                <h4>Got <a href="javascript:void(0);" onclick="formFeedback();">feedback</a>?</h4>
            </div>
        </div>
    </body>
</html>

