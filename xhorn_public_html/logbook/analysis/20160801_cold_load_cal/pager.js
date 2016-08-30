var pvp=[];

var fig=[];
function default_figname_fun() {
  fig=[];
}

var figname_fun=default_figname_fun;
function set_figname_fun(funname) {
  figname_fun=funname;
  figname_fun();
}

function onImgError(source){
  source.src = "no_image_available.jpg";
  //source.src = "no-image-100px.gif";
  //alert('No image available')
}

var param=[];

// Stolen from the internets
// http://www.greywyvern.com/?post=258
function splitCSV (instr,sep) {
  for (var foo = instr.split(sep = sep || ","), x = foo.length - 1, tl; x >= 0; x--) {
    if (foo[x].replace(/"\s+$/, '"').charAt(foo[x].length - 1) == '"') {
      if ((tl = foo[x].replace(/^\s+"/, '"')).length > 1 && tl.charAt(0) == '"') {
        foo[x] = foo[x].replace(/^\s*"|"\s*$/g, '').replace(/""/g, '"');
      } else if (x) {
        foo.splice(x - 1, 2, [foo[x - 1], foo[x]].join(sep));
      } else foo = foo.shift().split(sep).concat(foo);
    } else foo[x].replace(/""/g, '"');
  } return foo;
}

function td_colorate(oncol,offcol) {
  // List all the <td> tags in the document
  var tds=document.getElementsByTagName('td');
  for (var i=0; i<tds.length; i++) {
    var tmp=tds[i].innerHTML;
    // Ignore the ones that have other TDs inside them
    if (tmp.toLowerCase().indexOf("<td")!=-1) {
      continue
    }
    // Loop over them looking for set_params()
    var j=tmp.indexOf("set_params");
    if (j==-1) { continue }
    tmp=tmp.substring(j);
    j=tmp.indexOf("(");
    if (j==-1) { continue }
    var argstr=tmp.substring(j+1);
    argstr=splitCSV(argstr,')');
    if (argstr.length<2) { continue }
    argstr=argstr[0];
    argstr=splitCSV(argstr,',');
    if (argstr.length<2) { continue }
    for (var k=0; k<argstr.length; k++) {
      argstr[k]=argstr[k].replace(/['"]/g,'');
    }
    for (var k=0; k<argstr.length; k+=2) {
      // alert(argstr[k]+","+argstr[k+1]);
      if (param[argstr[k]] == argstr[k+1]) {
        tds[i].style.backgroundColor=oncol;
      } else {
        tds[i].style.backgroundColor=offcol;
      }
    }
  }
}

function linkrel_permify() {
  // List all the <a> tags in the document
  var as=document.getElementsByTagName('a');
  for (var i=0; i<as.length; i++) {
    var tmp=as[i].href;
    var j=tmp.indexOf("#permalink_");
    if (j==-1) { continue }
    tmp=tmp.substring(j);

    var new_url="?";
    for (var j in param) {
      new_url=new_url+"&"+j+"="+param[j];
    }
    as[i].href=new_url+tmp;
  }
}

var do_autocolor=0;
var on_color="Gray";
var off_color="LightGray";

function set_autocolor(onoff,oncol,offcol){
  do_autocolor=onoff;
  if (oncol != undefined)
    on_color=oncol;
  if (offcol != undefined)
    off_color=offcol;
}

function plupdate(){
  if (pvp.length>0) {
    for (var i=0; i<pvp.length; i++) {
      param[pvp[i].name]=pvp[i].val;
    }
    pvp=[];
  }
  figname_fun();
  for (i in fig) {
    document[i].src=fig[i].fname;
    if ((typeof fig[i].link == undefined) || (fig[i].link == undefined)) {
      fig[i].link=fig[i].fname;
    }
  }
  if (do_autocolor) {
    td_colorate(on_color,off_color);
  }
  linkrel_permify();
}

function set_params(){
  for (var i=0; i<arguments.length; i+=2) {
    param[arguments[i]]=arguments[i+1];
  }
  plupdate();
} 

var pager={};

function auto_pager(){
  // Get list of pager buttons to include
  if (arguments.length>0) {
    paramlist=arguments[0];
  } else {
    for (var i in pager) {
      paramlist.push(i);
    }
  }

  // Keep track of how many we've made
  if (typeof auto_pager.fignum == 'undefined') {
    auto_pager.fignum=0;
  }
  auto_pager.fignum++;

  // Get other options for style, etc.
  var style=1;
  var maxcols=0;
  var figname='fig'+auto_pager.fignum;
  var figtitle='Pager options';
  for (var i=1; i<arguments.length; i+=2) {
    switch(arguments[i].toLowerCase()) {
      case 'style': style=arguments[i+1]; break;
      case 'maxcols': maxcols=arguments[i+1]; break;
      case 'figname': figname=arguments[i+1]; break;
      case 'title': figtitle=arguments[i+1]; break;
      default: alert('Unrecognized auto_pager option '+arguments[i]);
    }
  }
  if (maxcols==0) {
    if (style==2) maxcols=4;
    else maxcols=1;
  }

  // Get max number of options in a single section
  var numcols=0;
  for (var i=0; i<paramlist.length; i++) {
    var tmp=Math.floor((pager[paramlist[i]].length-1)/2.0);
    if (tmp>numcols) numcols=tmp;
  }
  if (numcols<maxcols)
    maxcols=numcols;

  if (style==1) {
    document.write('<table border="0" cellpadding="0">\n');
    document.write('<tr><th colspan="'+maxcols+'">');
    if (figname=='') {
      document.write(figtitle);
    } else {
      document.write('<a name="permalink_'+figname+'" /><a href="#permalink_'+figname+'">'+figtitle+'</a>');
    }
    document.write('</th></tr>\n');
    for (var i=0; i<paramlist.length; i++) {
      document.write('<tr><td colspan="'+maxcols+'"><hr /></td></tr>\n');
      document.write('<tr><th colspan="'+maxcols+'">'+pager[paramlist[i]][0]+'</th></tr>\n');
      var k=0;
      for (var j=1; j<pager[paramlist[i]].length; j+=2) {
        if (k==0) {
          document.write('<tr>');
        } else {
          document.write('    ');
        }
        document.write('<td><a href="'+'javascript:set_params('+"'"+paramlist[i]+"','"+pager[paramlist[i]][j+1]+"');"+'">'+pager[paramlist[i]][j]+'</a></td>');
        k++;
        if (k>=maxcols) {
          document.write('</tr>');
          k=0;
        }
        document.write('\n');
      }
    }
    document.write('</table>\n');
  }
  else if (style==2) {
    var maxcolp1=maxcols+1;
    document.write('<table border="0" cellpadding="0">\n');
    document.write('<tr><th colspan="'+maxcolp1+'">');
    if (figname=='') {
      document.write(figtitle);
    } else {
      document.write('<a name="permalink_'+figname+'" /><a href="#permalink_'+figname+'">'+figtitle+'</a>');
    }
    document.write('</th></tr>\n');

    for (var i=0; i<paramlist.length; i++) {
      document.write('<tr><td colspan="'+maxcolp1+'"><hr /></td></tr>\n');
      var nrows=Math.ceil(Math.floor((pager[paramlist[i]].length-1)/2.0)/maxcols);
      document.write('<tr><th rowspan="'+nrows+'">'+pager[paramlist[i]][0]+'&nbsp;&nbsp;</th>\n');
      var k=0;
      for (var j=1; j<pager[paramlist[i]].length; j+=2) {
        if (k==0 && j>1) {
          document.write('<tr>');
        } else {
          document.write('    ');
        }
        document.write('<td>');
        if (pager[paramlist[i]][j]=='') {
          document.write('&nbsp;');
        } else {
          document.write('<a href="'+'javascript:set_params('+"'"+paramlist[i]+"','"+pager[paramlist[i]][j+1]+"');"+'">'+pager[paramlist[i]][j]+'</a>');
        }
        document.write('</td>');
        k++;
        if (k>=maxcols) {
          document.write('</tr>');
          k=0;
        }
        document.write('\n');
      }
    }
    document.write('</table>\n');
  }
}

// grab query words from URL
function get_query_words() {
  var query_string=window.location.search.substring(1);
  var query_words=query_string.split("&");
  var j=0;
  for (var i=0; i<query_words.length; i++) {
    onpvp=query_words[i].split("=");
    if (onpvp.length==2) {
      pvp[j]={};
      pvp[j].name=onpvp[0];
      pvp[j].val=onpvp[1];
      j++;
    }
  }
}
