<h1>Tools for eQTL visualization and investigation</h1>
<table>
<tr><td>Author:</td><td>Jiao Long, Wouter van der Schoot, Harm Nijveen, Basten Snoek</td></tr>
<tr><td>Email:</td><td><a href="mailto:jiao.long@wur.nl">jiao.long@wur.nl</a> <a href="mailto:harm.nijveen@wur.nl">harm.nijveen@wur.nl</a> <a href="mailto:basten.snoek@wur.nl">basten.snoek@wur.nl</a></td></tr>
<tr><td>Github:</td><td><a href="https://github.com/longing247/eQTL.git">git clone https://github.com/longing247/eQTL.git</a></td></tr>
</table>
<h2>Research questions</h2>
<h3>QTL visualization</h3>
<ul>
	<li>allow user upload eQTL datasets using a generalized module</li>
	<li>visualize eQTL mapping result through cis-/trans-eQTL plot
	<li>currently only accepts <i>Arabidopsis Thaliana</i> and <i>Caenorhabditis Elegans</i> datasets, but allows to expand the existing structure towards other species</li>
</ul>	
<h3>QTL investigation</h3>
<ul>
	<li>select candidate genes underlying a QTL</li>
	<li>disection of gene regulation network</li>
	<ul><li>identify co-regulated genes modules for a QTL</li>
	<li>GO enrichment analysis</li></ul>
</ul>
<h2>User stories</h2>
<h3>Register,login and logout</h3>
[developmental stage]:  
<ul> 
	<li>Register url: <a href="http://127.0.0.1:8000/register/">http://127.0.0.1:8000/register/</a></li>
	<li>Login url: <a href="http://127.0.0.1:8000/login/">http://127.0.0.1:8000/login/</a></li>
	<li>Logout via the link at upper right. You need to log in first.</li>
</ul>

<h3>eQTL datasets upload</h3>
Upload url: <a href="http://127.0.0.1:8000/upload/">http://127.0.0.1:8000/upload/</a>
Please choose the right species and fill in the experiment name with informative keywords e.g. Snoek_Terpstra_etal_2012.
It also takes as argument files containing:
<ul>
	<li>Array spot/transcript information</li>
	<li>Marker information</li>
	<li>LOD file from eQTL mapping</li>
	<li>Optional: Genotype information</li>
</ul>
Those files will be automaticly renamed and stored in the media folder under the root of project folder.
<p>Sample datesets [developmental stage]:
<p><a href="http://127.0.0.1:8000/media/data/Joosen_etal_2012/array.txt">Array file</a></p>
<p><a href="http://127.0.0.1:8000/media/data/Joosen_etal_2012/marker.txt">Marker file</a></p>
<p><a href="http://127.0.0.1:8000/media/data/Joosen_etal_2012/genotype.txt">Genotype file</a></p>
<p><a href="http://127.0.0.1:8000/media/data/Joosen_etal_2012/lod.txt">LOD file</a></p>

<h3>eQTL mapping result visualizatioin</h3>
eQTL visualization url: <a href="http://127.0.0.1:8000/visualization/">http://127.0.0.1:8000/visualization/</a>
By selecting an experiment, the cis-/trans-eQTL plot will be generated on the fly using pretreated lod.json file (FDR a=0.05) and probe files.
The cis-/trans-eQTL plot was adopted from D3 interative examples published by Karl Broman with changes.
<ul><li>mouse over a eQTL: a tooltip will be showed with QTL information (transcript,marker.and etc); More detailed information is available in the adjacent QTL info module.</li>
<li>mouse click a eQTL: LOD profile plot will be synchronized for the eQTL.</li>
</ul>
You may add one or more QTL instances to the user session module for further analysis.
<h3>co-expressed co-regulated genes for a QTL</h3>
eQTL investigation url: <a href="http://127.0.0.1:8000/investigation/">http://127.0.0.1:8000/investigation/</a>
<p>If the page is rendered without pre-selected QTLs, you may need to fill in experiment name, marker refers a QTL of interest and LOD threshold. With those information, numbers of co-regulated genes for the given QTL can be retrived and use to compare with a user defined gene list from input (multiple delimiter ',',';','\t',' ' are supported) or a file</p>
<p>If the page is rendered with pre-selected QTLs, you may directly use them for comparison.</p>

<h3>candidates genes for a QTL</h3>
eQTL investigation url: <a href="http://127.0.0.1:8000/investigation/">http://127.0.0.1:8000/investigation/</a>
<p>For a give trait for a QTL, 1-LOD support interval will be used to defined the confidence interval. Base on the confidence interval, genes underlying the mapped genomic region can be returned. You may want to use those genes to compare with the candidate genes for a QTL in another experiment </p>
<h3>Go enrichment analysis</h3>
<p>goatools is integrated for gene enrichment analysis. https://github.com/tanghaibao/goatools</p>
<p>A number of co-regulated genes for a QTL returned from investigation can be used for GO enrichment analysis, based on Fisher's exact test. It also implemented several multiple correciton routines(including Bonferroni, Sidak, and false discovery rate).</p>
<p>dependencies: obo-formatted file (go-basic.obo) from Gene ontology website, and gene-GO association file.</p>
<p>sample gene-GO association file: <a href="http://127.0.0.1:8000/media/association/Arabidopsis Thaliana/association.txt">association file</a></p>  
