        <!-- feedback form -->
        <script type='text/javascript'>
        function formFeedback() {
            var formUrl = "https://docs.google.com/forms/d/1YNODxi35XiJEv80wOJDFV3H2IIfOYmU3K5hCU8SfunE/viewform?entry.229836285=" + encodeURIComponent(location.href);
                window.open(formUrl);
        }
        </script>

	<script type='text/javascript'>
	$(document).ready(function() {
            var data='<?php print $_GET["query"] ?>';
	    var bento_url = "http://gwbento-test.wrlc.org/";

	    function fetch(vals) {
                $.get(bento_url+vals[0],
                      {"q": data,
                       "remote_addr": "<?php echo $_SERVER["REMOTE_ADDR"] ?>"},
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
            for (var i=0; i < blocks.length; i++) {
                fetch(blocks[i]);
            }
	});
	</script>

<?php if ($_GET["query"])
{
?>
<div class='search-all-banner-outer'>
  <div id='form' class='search-all-banner'>
    <div class='search-all-banner-inner' style=''>
      <form action='search-beta' method='GET' class='search-form'>
            <div class='search-all-label'><label>Search All</label></div>
            <div class='search-all-form-fields'>
            <input id='query' type='text' size='40' name='query' value='<?php print $_GET["query"] ?>' />
            <input type='submit' value='Search'/>
            </div>
      </form>
    </div>
  </div>
</div>
<div id='results' class='row-fluid'>
    <div id='bestbets-articles-databases' class='span4'>
        <h2 id='bestbets-title' style='display:none;'>Best Bets</h2>
        <div id='bestbets-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <h2>Articles</h2>
        <div id='articles-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr />
        <h2>Databases</h2>
        <div id='databases-solr-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr class="mobile-show-720" />
    </div>
    <div id='books-journals' class='span4 left-border'>
        <h2>Books &amp; Media</h2>
        <div id='books-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr />
        <h2 class='separate-top'>Journals</h2>
        <div id='journals-solr-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr class="mobile-show-720" />
    </div>
    <div id='website-other' class='span4 left-border'>
        <h2>Library Website</h2>
        <div id='libsite-response' class='row-fluid'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <hr />
        <h2>Research Guides</h2>
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

