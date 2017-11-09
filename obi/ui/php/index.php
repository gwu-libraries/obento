        <!-- feedback form -->
        <script type='text/javascript'><!--
        function formFeedback() {
            // TEST form - uncomment for TEST
            var formID = "1YNODxi35XiJEv80wOJDFV3H2IIfOYmU3K5hCU8SfunE";
            // PRODUCTION form - uncomment for PRODUCTION
            // var formID = "1zTbNA6_4urOuEAjcCJrGBqZD8JVY3xxqTIaHP44YHOA";
            var formUrl = "https://docs.google.com/forms/d/" + formID + "/viewform?entry.229836285=" + encodeURIComponent(location.href);
                window.open(formUrl);
        }
        --></script>

        <script type='text/javascript' src="https://cdnjs.cloudflare.com/ajax/libs/jquery-ajaxtransport-xdomainrequest/1.0.1/jquery.xdomainrequest.min.js"></script>

	<script type='text/javascript'><!--
	(function($) {
	var searchid;
	var data;
	var ignoresearch;
	var count;
	var bento_url;
	var remote_addr = "<?php echo $_SERVER["REMOTE_ADDR"] ?>";
	function fetch(vals){
	    if(count == "0" || !/^\d+$/.test(count)){
		$.get(bento_url+vals[0],
                        {"q": data,
			 "searchid": searchid,
                        "ignoresearch": ignoresearch,
                        "remote_addr": remote_addr},
                        function(response){
                            $(vals[1]).html(response);
                        }
                     );
	    }
	    else{
		 $.get(bento_url+vals[0],
                        {"q": data,
                         "searchid": searchid,
                        "ignoresearch": ignoresearch,
                        "count": count,
                        "remote_addr": remote_addr},
                        function(response){
                            $(vals[1]).html(response);
                        }
                    );

	    }
	
	}
	$(document).ready(function() {
            data="<?php if (isset($_GET["query"])) {print addslashes($_GET["query"]);} ?>";
	    data = data.trim();
            ignoresearch="<?php if (isset($_GET["ignoresearch"])) {print addslashes($_GET["ignoresearch"]);} else {print "false";}?>";
            count="<?php if (isset($_GET["count"])) {print $_GET["count"];} else {print "0";}?>";
            <?php
  	      // checks to see if function exists and sets the Bento target (set in GW custom Catalog Pointer module) and if not sets a default value (the prod Bento server).
  	      if (function_exists('catalog_pointer_bento')) {$bentoTarget = catalog_pointer_bento();} else {$bentoTarget = "http://bento.library.gwu.edu/";} 
	    ?>
            bento_url = "<?php echo $bentoTarget; ?>";
	    var save_data_url = "save_data";
	    function save_query(save_data_url){
		$.get(bento_url+save_data_url,
                        {"q": data,
                        "ignoresearch": ignoresearch,
                        "remote_addr": remote_addr},
                        function(response){
                            var info = JSON.parse(response);
			    searchid = info.searchid;
			    load_bento_boxes();
                        }
                    );
    	     };
    	     save_query(save_data_url);
	});
function load_bento_boxes(){
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
}
	})(jQuery);
	--></script>

<div class='search-all-banner-outer'>
  <div id='form' class='search-all-banner'>
    <div class='search-all-banner-inner' style=''>
      <form action='search-beta' method='GET' class='search-form'>
            <div class='search-all-label'><label>Search All</label></div>
            <div class='search-all-form-fields'>
            <input aria-label='Enter your search terms' id='query' type='text' size='40' maxlength='100' name='query' value='<?php
if(isset($_GET["query"]))
   print htmlspecialchars($_GET["query"], ENT_QUOTES);
?>'
autocomplete='off' autocorrect='off' autocapitalize='off' spellcheck='false' />
            <input type='submit' value='Search'/>
            </div>
      </form>
    </div>
  </div>
 <div id='dym' style=' margin-left: 13px;padding-top: 0; padding-bottom: 0.6em;'></div>
</div>
<?php if (isset($_GET["query"]))
{
?>

<div class="mobile-show-720 row-fluid">
  <div class="span12">
    <div>Results by:</div>
    <div class="bento-jumpto"><a href="#articles"><button>Articles</button></a><a href="#databases"><button>Databases</button></a><a href="#books-media"><button>Books & Media</button></a><a href="#journals"><button>Journals</button></a><a href="#website"><button>Website</button></a><a href="#research-guides"><button>Research Guides</button></a></div>
  </div>
</div>

<div id='results' class='row-fluid'>

    <div id='bestbets-articles-databases' class='span4'>

      <div id='bestbets-title' class='result-card' style='display:none;'>
        <h2>Best Bets</h2>
        <div id='bestbets-response'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
      </div>

      <div id='articles' class='result-card'>
        <h2>Articles</h2>
        <div id='articles-response'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <!--<hr />-->
      </div>

      <div id='databases' class='result-card'>
        <h2>Databases</h2>
        <div id='databases-solr-response'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <!--<hr class="mobile-show-720" />-->
      </div>

    </div>

    <div id='books-journals' class='span4 left-border'>

      <div id='books-media' class='result-card'>
        <h2>Books &amp; Media</h2>
        <div id='books-response'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <!--<hr />-->
      </div>

      <div id='journals' class='result-card'>
        <h2 class='separate-top'>Journals</h2>
        <div id='journals-solr-response'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <!--<hr class="mobile-show-720" />-->
      </div>

    </div>

    <div id='website-other' class='span4 left-border'>

      <div id='website' class='result-card'>
        <h2>Library Website</h2>
        <div id='libsite-response'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
        <!--<hr />-->
      </div>

      <div id='research-guides' class='result-card'>      
        <h2>Research Guides</h2>
        <div id='guides-response'>
            <div class='span2 progress progress-striped active'>
                <div class='bar' style='width: 100%;'></div>
            </div>
        </div>
      </div>

    </div>

</div>
<?php
}
?>

<div class='row-fluid' style="margin-top:3em;">
  <div class="span12 feedback-link">
    <a href="javascript:void(0);" onclick="formFeedback();"><button>Got feedback ?</button></a>
  </div>
</div>
