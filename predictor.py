# scheme://netloc/path?query#fragment
import os
import sys
import warnings
import logging
import absl.logging
import ydf
import contextlib

from collections import Counter
from datetime import datetime, timezone
import ipaddress
# import pickle
import joblib
import re
from urllib.parse import urlparse
from scipy.stats import entropy
import pandas as pd
import numpy as np
import tldextract
import whois
import os
import ydf


MY_SHORTENERS = {'synd.co', 'tonyr.co', 'clicky.me', 'cadill.ac', 'skr.rs', 'minilink.io', 'redaz.in', 'tlil.nl', 'abe.ma', 'ntuc.co', 'sumal.ly', 'bbva.info', 'shorten.world', 'goolink.cc', 'lihi.biz', 'cb.com', 'grm.my', 'go.dbs.com', 'tg.pe', 'zaya.io', 'utraker.com', 'learn.to', 'p1r.es', 'pdora.co', 'aet.na', 'sn.rs', 'tnvge.co', 'eepurl.com', 'zlw.re', 'urbn.is', 'bhpho.to', 'tny.cz', 'go.aws', 'mklnd.com', 'jpeg.ly', 'ul3.ir', 'mcgam.es', 'cathaysec.tw', 'cultm.ac', '98pro.cc', 'oxelt.gl', 'bbc.in', 'dvrv.ai', 'zc.vg', 'mzl.la', '6.ly', 'foodtv.com', 'ff.im', 'yun.ir', 'ibm.co', 'ti.me', 'pepsi.co', '5.gp', 'y2u.be', 't.iotex.me', 'fxn.ws', 'go.sony.tw', 'bfpne.ws', 'redsto.ne', 'z23.ru', 'mgnet.me', 'mybmw.tw', 'rol.st', 'garyvee.com', 'wun.io', 'on.ft.com', 'starz.tv', 'kurl.ru', 'omni.ag', 'livemu.sc', 'tsta.rs', 'gizmo.do', 'gjk.id', 'il.rog.gg', 'captl1.co', 'ana.ms', 'we.co', 'zopen.to', 'mnge.it', 'mylt.tv', 'gh.io', 'lihi3.me', '1drv.ms', 'ppt.cc', 'ezstat.ru', 'trib.al', 'gtne.ws', 'tny.im', 'tlrk.it', 'biggo.tw', 'shp.ee', 'ipgraber.ru', 'lnk.sk', 'wwf.to', 'itsh.bo', 'mypoya.com', 'bigfi.sh', 'indeedhi.re', 'nflx.it', 'b-gat.es', 'lt27.de', 'socx.in', 'gfuel.ly', 'iplwin.us', 'walk.sc', 'dopice.sk', 'gowat.ch', 'stts.in', 'lihi1.cc', 'tgam.ca', 'ind.pn', 'xrds.ca', 'atm.tk', 'bca.id', 'vbly.us', 'intel.ly', 'prgress.co', 'lihipro.com', 'onforb.es', 'cplink.co', 'ourl.tw', 'gma.abc', 'mney.co', 'alli.pub', 'centi.ai', 'pa.ag', 'boile.rs', 'ludia.gg', 'migre.me', 'rozhl.as', 'sail.to', 'tmz.me', 'fandan.co', 'zurb.us', 'asin.cc', 'cbj.co', 'seedsta.rs', 'atmlb.com', 'mck.co', 'fandom.link', 'gph.to', 'amrep.org', 'conta.cc', 'goo-gl.me', 'amba.to', 'ctbc.tw', 'kg.games', 'eslite.me', 'replug.link', 'glblctzn.me', 'avlne.ws', 'youtu.be', 'lin.ee', 'lmy.de', 'ul.to', 'ko.gl', 'ela.st', 'hf.co', 'lnv.gy', 'zecz.ec', 'suo.im', 'lat.ms', '71a.xyz', 'urls.fr', 'siriusxm.us', 'rsh.md', 'twou.co', 'dxc.to', 'faras.link', 'flomuz.io', 'ghkp.us', 'xor.tw', 'urls.kr', 'skimmth.is', 'mstr.cl', 'forr.com', 'p.dw.com', 'warp.plus', 'tnw.to', 'oe.cd', 'm1p.fr', 'shorten.asia', 'linkye.net', 'ritea.id', 'clvr.rocks', 'cvent.me', 'klck.me', 'shrtm.nu', 'pplx.ai', 'oxf.am', 'ky77.link', 'lnkiy.in', 'liip.to', 'apple.co', 'svy.mk', 'yubi.co', 'andauth.co', 'hill.cm', 'go.btwrdn.co', 'zez.kr', 'sched.co', 'act.gp', 'autode.sk', 'travl.rs', 'trymongodb.com', 'petrobr.as', 'thls.co', 'wpbeg.in', 'dkng.co', '9splay.store', 'elle.re', 'spr.ly', 'cnb.cx', 'vxn.link', 'anyimage.io', 'firsturl.net', 'aka.ms', 'fb.me', 'abre.ai', 'tpmr.com', 'cle.clinic', 'lnk.do', 'pojonews.co', 'kck.st', 'b2n.ir', 'urt.io', 'wrem.it', 'linkbun.com', 'sk.in.rs', 'nkbp.jp', 'tmblr.co', 'myumi.ch', 'n.pr', 'supr.link', 'aptg.tw', 'tgr.ph', 'tt.vg', 'kl.ik.my', 'go.edh.tw', 'shorturl.asia', 'yadi.sk', 'tr.ee', 'cin.ci', 'dcps.co', 'nyr.kr', 'cnfl.io', 'rtvote.com', 'lonerwolf.co', 'f1.com', 'ouo.io', 'comca.st', 'go.intigriti.com', 'qnap.to', 'da.gd', 'scr.bi', 'suo.fyi', 'rblx.co', 'urlz.fr', 'amzn.pw', 'tibco.co', '1shop.io', 'ringcentr.al', 'shorturl.ae', 'cna.asia', 's.ee', 'al.st', 'github.co', 'mvmtwatch.co', 'lihivip.com', 'lihi2.cc', 'fam.ag', 'q.gs', 'xerox.bz', 'rsc.li', 'notlong.com', 'wbze.de', 'fav.me', 'insig.ht', 'fstrk.cc', 'aon.io', 'gen.cat', 'kkc.tech', 'go.tinder.com', 'okt.to', 'zurl.co', 'hulu.tv', 'pr.tn', 'uk.rog.gg', 'kgs.link', 'bonap.it', 'f5yo.com', 'lmg.gg', 'tvote.org', 'pin.it', 'dbricks.co', 'glmr.co', 'oyn.at', 'godrk.de', 'tokopedia.link', 'dailym.ai', 'wef.ch', 'ford.to', '3.cn', 'loom.ly', 'go.nasa.gov', 'apple.news', 'bitly.lc', 'toi.in', 'scrb.ly', 'zurl.ir', 'sc.mp', 'efshop.tw', 'small.cat', 'wa.link', 'btm.li', 'bcene.ws', 'fn.gg', 'llo.to', 'onelink.to', 'minify.link', 'ul.rs', 'instagr.am', '49rs.co', 'sforce.co', 'to.ly', 'gym.sh', 'kas.pr', 'psee.io', 'opr.as', 'booki.ng', 'luminary.link', 'vo.la', 't-bi.link', 'sho.pe', 'do.co', 'alpha.camp', 'name.ly', 'goo.gl', 'dd.ma', 'xprt.re', 'wee.so', 'dk.rog.gg', 'smlk.es', 'cbt.gg', 'm.tb.cn', 'soc.cr', 's.uniqlo.com', 'skrat.it', 'cathaybk.tw', '101.gg', 'adbl.co', 'lft.to', 'piee.pw', 'pnsne.ws', 'syb.la', 'link.tubi.tv', 'tibco.cm', 'circle.ci', 'rethinktw.cc', 'blizz.ly', 'disq.us', 'meck.co', '2.ly', 'git.io', 'mpl.pm', 'mub.me', 'thn.news', 'nej.md', '6g6.eu', '301.link', 'gq.mn', 'dv.gd', 'simp.ly', 'sqrx.io', 'go.jc.fm', 'acer.co', 'on9news.tv', 'rizy.ir', 'ix.sk', 'tdrive.li', 'acortar.link', 'tinylink.net', 'latingram.my', 'tim.com.vc', 'hyperurl.co', 'pxu.co', 'zxc.li', 'wndrfl.co', 'wwp.news', '1kh.de', 'psce.pw', 'p.asia', 'gbod.org', 'lihi1.me', 'aarp.info', 'sbux.jp', 'bzfd.it', 'fal.cn', 'momo.dm', 'rdcu.be', 'bstk.me', 'atmilb.com', 'edin.ac', 'whoel.se', 'tidd.ly', 'cort.as', 'g.page', 'cc.cc', 's.ul.com', 'citi.asia', 'zi.ma', 'sokrati.ru', 'gdurl.com', 'unc.live', 'ept.ms', 'ht.ly', 'go.rebel.pl', 'urlgeni.us', 'firsturl.de', 'ubnt.link', 'zdrive.li', 'gov.tw', '707.su', 'relink.asia', 'ufcqc.link', 'davidbombal.wiki', 'hpe.to', 'haa.su', 'sfcne.ws', 'exitl.ag', 'mbapp.io', 'kkday.me', 'peoplem.ag', 'lnk.bz', 'man.ac.uk', 'cyb.ec', 'kbank.co', 'alturl.com', 'dy.si', 'nswroads.work', 'lc.cx', 'envs.sh', 'mcys.co', 'spoti.fi', 'discord.gg', 'nyti.ms', 'spr.tn', 'w.idg.de', 'krazy.la', 'lego.build', 'mo.ma', 'rfr.bz', 'grnh.se', 'wapo.st', 'bmai.cc', 'shorten.is', 'uoft.me', 'agrd.io', 'jz.rs', 'klmf.ly', 'ubr.to', 'fltr.ai', 'tinyurl.hu', 'cart.mn', 'careem.me', '2pl.us', '12ne.ws', 'txdl.top', 'ume.la', 'dub.sh', 'readhacker.news', 'fumacrom.com', 'cnet.co', 'shorturl.com', 'spotify.link', 'deli.bz', 'optimize.ly', 'rch.lt', 'come.ac', 'bzh.me', 'etoro.tw', 'seagate.media', 'ptix.co', 'mork.ro', 'clickmeter.com', 'arc.ht', 'smarturl.it', 'purefla.sh', 'tinyarro.ws', 'beats.is', 'ibb.co', 'jcp.is', 'arah.in', 'rdbl.co', 'by2.io', 'on.natgeo.com', 'nbcnews.to', 'han.gl', 'j.mp', 'tiny.one', 'on.nypl.org', 'utn.pl', 'wn.nr', 'anch.co', 'esqr.co', 'nbzp.cz', 'arkinv.st', 'lnkiy.com', 'vntyfr.com', 'moo.im', 'politi.co', 'geti.in', 'tnne.ws', 'b23.tv', 'rnm.me', 'srnk.us', 'ref.trade.re', 'asus.click', 'ibm.biz', '3le.ru', 'zuki.ie', 'br4.in', 'propub.li', 'on.nyc.gov', 'clr.tax', 'ngrid.com', 'dems.me', 'asics.tv', 'tw.rog.gg', 'rpf.io', 'lyksoomu.com', 'fnb.lc', 'yal.su', 'outschooler.me', 'redir.ec', 'ln.run', 'epochtim.es', 'my.mtr.cool', 'rly.pt', 'reurl.cc', 'caro.sl', 'munbyn.biz', 'dssurl.com', 'cookcenter.info', 'meetu.ps', 'pipr.es', 'gandi.link', 'urluno.com', 'cnn.it', 'blstg.news', 'ow.ly', 'cybr.rocks', 'goo.by', 'qrs.ly', 'nav.cx', 'shar.as', 'philips.to', '92url.com', 'pgrs.in', 'w.wiki', 'crdrv.co', 'tinyurl.mobi', 'metamark.net', 'whi.ch', 'lihi.vip', 'kham.tw', 'gek.link', 'can.al', 'thinfi.com', 'everri.ch', 'flx.to', 'pxgo.net', 'ukf.me', 'nokia.ly', 'bl.ink', 'ja.cat', 'xpr.li', 'me2.kr', 'ifix.gd', 'bookstw.link', 'wbby.co', 'wooo.tw', 'mttr.io', 'wartsi.ly', 'b.mw', 'bddy.me', 'dee.pl', 'ellemag.co', 't.co', 'yip.su', 'abr.ai', 'stanford.io', 'popm.ch', 'siteco.re', 'zeep.ly', 'dhk.gg', '2kgam.es', 'snyk.co', 'xrl.us', 'walkjc.org', 'shorten.tv', 'splk.it', 's.accupass.com', 'nbc4dc.com', 'hicider.com', 'linkd.in', 'ppurl.io', 'to.pbs.org', 'stmodel.com', '7oi.de', 'fox.tv', 'n.opn.tl', 'ta.co', '89q.sk', 'regmovi.es', 'u.to', 'ebay.to', 'bytl.fr', 'kortlink.dk', 'urly.co', 'intuit.me', 'lih.kg', 'smsng.news', 'adm.to', 'enshom.link', 'zpr.io', 'lzd.co', 'uofr.us', 'sprtsnt.ca', 'lihi3.com', 'aje.io', 'tinyurl.com', 'cbsn.ws', 'cut.lu', 'trade.re', 'whatel.se', 'waa.ai', 'wrctr.co', 'wp.me', 'st.news', 'sfty.io', 'zzb.bz', 'acus.org', 'myglamm.in', 'vvnt.co', 'go.qb.by', 'icks.ro', 'rem.ax', 'ntn.so', '985.so', 'goolnk.com', 't1p.de', 'wa.sv', 'tcrn.ch', 'inlnk.ru', '5w.fit', 'urb.tf', 'bitly.com', 'nchcnh.info', 'volvocars.us', 'go.osu.edu', 'cutt.ly', 'wb.md', 'pg3d.app', 'forms.gle', 'rvwd.co', 'hubs.li', 'ii1.su', 'sinourl.tw', 'imdb.to', 'swoo.sh', 'plu.sh', 'ctfl.io', 'msi.gm', 'sc.org', 'zurins.uk', 'toyota.us', 'bityl.co', 'ai6.net', 'adweek.it', 'myurls.ca', 'alexa.design', 'opr.news', 'thght.works', 'pwc.to', 'katzr.net', 'saf.li', 'aol.it', 'skl.sh', 'sht.moe', 'htl.li', 'ryml.me', 'ic9.in', 'itvty.com', 'bg4.me', 'amzn.com', 'linkopener.co', 'thedo.do', 'ckbe.at', 'pchome.link', 'dtdg.co', 'l8r.it', 'usanet.tv', 'abc7.la', 'gtly.to', 'kutt.it', 'mbayaq.co', 'chts.tw', 'yex.tt', 'fevo.me', 'ock.cn', 'd-sh.io', 'href.li', 'myppt.cc', 'bayareane.ws', 'huma.na', 'shiny.link', 'kuku.lu', 'urlr.me', 'ur3.us', 'ntap.com', 'browser.to', 'troy.hn', 'rog.gg', 'swa.is', 'redir.is', '8.ly', 'discvr.co', 'hp.care', 'iqiyi.cn', 'wrd.cm', 'app.philz.us', 'genie.co.kr', 'ofcour.se', 'weall.vote', 'a360.co', 'ukoeln.de', 'fa.by', '1url.cz', 'orlo.uk', 'pod.fo', 'avlr.co', 'bit.ly', 'obank.tw', 'x.gd', 'bom.so', 'nature.ly', 'st8.fm', 'reut.rs', 'lativ.tw', 'inx.lv', 'oshko.sh', 'accu.ps', 'prn.to', 'cirk.me', 'nydn.us', 'rwl.io', 'kp.org', 'go.ly', 'histori.ca', 'edu.nl', 'lam.bo', 'xfin.tv', '4sq.com', 'fwme.eu', 'illin.is', 'bravo.ly', 'naver.me', '2.gp', 'amz.run', 'tw.sv', 'mrx.cl', 'onion.com', 's.coop', 'vivo.tl', 'ab.co', 'url2.fr', 'indy.st', 'flip.it', 'thr.cm', 'pt.rog.gg', 'bung.ie', 'blur.by', 'bnds.in', 'mnot.es', 'sdut.us', 'budurl.com', 'yourls.org', 'ionos.ly', 'dis.tl', 'pew.org', 'go.id.me', 'ua.rog.gg', 'kask.us', 'ity.im', 'abc7.ws', 'iplogger.ru', 'tdy.sg', 'chn.lk', 'vur.me', 'pdxint.at', 'tanks.ly', 'sie.ag', 'go.shell.com', 'fifa.fans', 'puri.na', 'a.189.cn', 'ssur.cc', 'thrill.to', 'tiny.pl', 'thetim.es', 'rd.gt', 'hmt.ai', 'fave.co', 'ulvis.net', 'dw.com', 'j.gs', 'tl.gd', 'rev.cm', 'short.gy', 'shorten.so', 'pse.is', 'flq.us', 'u.shxj.pw', 'lihi.pro', 'trackurl.link', 'lihi1.com', 'atres.red', '2.ht', 'hbom.ax', 'tmsnrt.rs', 'hrbl.me', 'zdsk.co', 'biibly.com', 'ourl.co', 'at.vibe.com', 'snd.sc', 'irng.ca', 'dai.ly', 'ro.blox.com', 'sourl.cn', 'lnk.direct', 'ed.gr', 'gaw.kr', 'wo.ws', 'flic.kr', 'jb.gg', 'gldr.co', 'blck.by', 'umlib.us', 'qr.ae', 'spigen.co', 'htn.to', 'nyer.cm', 'on.bp.com', 'www.shrunken.com', 'revr.ec', 'shorten.ee', 'coop.uk', 'renew.ge', 'nbcchi.com', 'gosm.link', 'dtsx.io', 'social.ora.cl', 'lin0.de', 'prdct.school', 'ubm.io', 'stuf.in', 'tnsne.ws', 'shln.me', 'crwd.fr', 'cmy.tw', 'maga.lu', 'es.rog.gg', 'gigaz.in', 'dky.bz', 'dainik-b.in', 'sck.io', 'on.fb.me', 'chl.li', 'bo.st', 'posh.mk', 'wmojo.com', 'homes.jp', 'adobe.ly', 'hubs.ly', 'casio.link', 'lemde.fr', 'zynga.my', 'on.wsj.com', 'sbux.co', 'on.tcs.com', 'htgb.co', 'seq.vc', 'crwd.in', 'oow.pw', 'sfca.re', 'acer.link', 'rushgiving.com', 'maper.info', 'bloom.bg', 'taiwangov.com', 'netm.ag', 'dlsh.it', '2u.lc', 'abnb.me', 'nxb.tw', 'fandw.me', 'y.ahoo.it', 'ntck.co', 'vonq.io', 'ocul.us', 'u.nu', 'got.cr', 'wellc.me', 'crwdstr.ke', 'cmu.is', 'adfoc.us', 'utm.to', 'swtt.cc', 'zywv.us', 'frdm.mobi', 'mz.cm', 'kkstre.am', 'ift.tt', 'sinyi.in', 'smashed.by', 'l.prageru.com', 'urlify.cn', 'rzr.to', 'go.intel-academy.com', 'owy.mn', 'ay.gy', 'hbaz.co', 'pzdls.co', 'storycor.ps', 'packt.link', 'i.coscup.org', 'dibb.me', 'mysp.ac', 'sgq.io', 'fmurl.cc', 'tiny.cc', 'rlu.ru', 'iln.io', 'on.ny.gov', 'sbird.co', 'dockr.ly', 'abc.li', '0a.sk', 'sina.lt', 'vodafone.uk', 'bigcc.cc', 'tbb.tw', 'nkf.re', 'gbte.tech', 'onepl.us', 'her.is', 'oran.ge', 'glo.bo', 'rdcrss.org', 'gi.lt', 'sf3c.tw', 'fooji.info', 'datayi.cn', 'clc.to', 'cnnmon.ie', 'url.cn', 'safelinking.net', 'oal.lu', 'bcsite.io', 'nycu.to', 'thefp.pub', 'xqss.org', 'jkf.lv', 'ourl.in', 'waad.co', 'lnky.jp', 'livestre.am', 'weare.rs', 'whr.tn', 'linkjust.com', 'cstu.io', 'k-p.li', 'onx.la', 'us.rog.gg', 'qr.net', 'fbstw.link', 'hi.sat.cool', 'ovh.to', 'link.ac', 'refini.tv', 'o.vg', 'apne.ws', 'ga.co', 'embt.co', 'nwppr.co', 'trt.sh', 'hubs.la', 'cs.co', 'trib.in', 'tny.so', 'go.lamotte.fr', 'skyurl.cc', 'gomomento.co', 'pl.kotl.in', '7.ly', 'clc.am', 'abcn.ws', 'merky.de', 'viraln.co', 'xfl.ag', '7news.link', 'mgstn.ly', 'zlr.my', 'twb.nz', '1ea.ir', 'chzb.gr', 'hashi.co', 'n9.cl', 'dpo.st', 'nxdr.co', 'amays.im', 'dmdi.pl', 'kf.org', '53eig.ht', 'eqix.it', 'infy.com', 'fb.watch', '4.gp', 'ibf.tw', 'm.me', 'm101.org', 'aces.mp', 'pgat.us', 'boa.la', 'etsy.me', 'your.ls', 'lihi2.com', 'nbcbay.com', 'cli.re', 'v.redd.it', 'g-web.in', 'poie.ma', 'thd.co', 'zln.do', 'bp.cool', 'cr8.lv', 'ftnt.net', 'pens.pe', 'ms.spr.ly', 'es.pn', 'yourwish.es', 'spcne.ws', 'isw.pub', 'on.nba.com', 'rb.gy', 'wahoowa.net', 'se.rog.gg', 'lihi.cc', 'vk.cc', 'rip.city', 'gtnr.it', 'mou.sr', 'zurl.ws', 'ter.li', 'vk.sv', 'thatis.me', 'shope.ee', 'lihi2.me', 'kings.tn', 'c87.to', 'r.zecz.ec', 'nnn.is', 'cfl.re', '2u.pw', 'dpmd.ai', 'brief.ly', 'cdl.booksy.com', 'url.ie', 'jnfusa.org', 'me.sv', 'go.hny.co', 'sdu.sk', 'wjcf.co', 'clarobr.co', 'rbl.ms', 'p4k.in', 'pck.tv', 'neti.cc', 'vercel.link', 'fce.gg', 'kkne.ws', 'linkshare.pro', 'deloi.tt', '5du.pl', 'tsbk.tw', 'emirat.es', 'boston25.com', 'mayocl.in', 'exe.io', 'wcha.it', 'redd.it', 'iplogger.info', 'lbtw.tw', 'nus.edu', 'mitsha.re', 'cut.pe', 'urly.fi', 'u1.mnge.co', 's04.de', 'fvrr.co', 'ucla.in', 'vypij.bar', 'sejr.nl', 'ilnk.io', 'vi.sa', 'gtly.ink', 'dmreg.co', 'temu.to', 'many.at', 'i.mtr.cool', 'zuplo.link', 'linko.page', 'ancstry.me', 'undrarmr.co', 'wit.to', 'cmon.co', 'squ.re', 'nr.tn', 'xurl.es', 'a.co', 'tpc.io', 'qptr.ru', 'xbx.lv', 'way.to', 'yelp.to', 'adaymag.co', 'sincere.ly', 'njersy.co', 'up.to', 'soch.us', '3.ly', 'go.vic.gov.au', 'stspg.io', 'mrte.ch', 'hideout.cc', 'mng.bz', 'reconis.co', 'sealed.in', 'wbur.fm', 'kpmg.ch', 'laco.st', 'lttr.ai', 'mapfan.to', 'nmrk.re', 'escape.to', 'txul.cn', 'goo.gle', 'so.arte', 'wkf.ms', '1un.fr', 'cl.ly', 'kfrc.co', 'go.ustwo.games', 'econ.st', 'rptl.io', 'mcd.to', 'anon.to', 'amzn.to', 'qrco.de', 'seiu.co', 'syw.co', 'link.infini.fr', 'spgrp.sg', 'sndn.link', 'swag.run', 'hi.switchy.io', 'canon.us', 't.libren.ms', 'di.sn', 'gmj.tw', 's3vip.tw', 'rebrand.ly', 'yji.tw', 'httpslink.com', 'asq.kr', 'win.gs', 'pewrsr.ch', 'herff.ly', 'zoho.to', 'pesc.pw', '69run.fun', 'offs.ec', 'twm5g.co', 'links2.me', 'esun.co', 'shorturl.at', 'icit.fr', 'getf.ly', 'red.ht', 'i-d.co', 'preml.ge', 'found.ee', 'hi.kktv.to', 'sdpbne.ws', 'snip.link', 't.ly', 'bridge.dev', 'uni.cf', 'sinyi.biz', 'sou.nu', 'thein.fo', 'go.shr.lc', '7ny.tv', 'iherb.co', 'smtvj.com', 'axoni.us', 'kotl.in', 'osdb.link', 'ampr.gs', 'cindora.club', 'benqurl.biz', 'gbpg.net', 'tprk.us', 't.tl', 'ihr.fm', 'safl.it', 'vtns.io', 'capital.one', 't.cn', 'zcu.io', 'brook.gs', 'voicetu.be', 'cbsloc.al', 'shorl.com', 'ipgrabber.ru', 'cjky.it', 'offf.to', 'michmed.org', 'cnvrge.co', 'go.usa.gov', 'owl.li', 'zovpart.com', 'blbrd.cm', 'nnna.ru', '9mp.com', '0.gp', 'zzu.info', 'hnsl.mn', 'blap.net', 'topt.al', 'lurl.cc', 'rotf.lol', 'wi.se', 'yhoo.it', 'zlra.co', '17mimei.club', 'zd.net', 'abc11.tv', 'axios.link', '2nu.gs', 'chn.ge', 'on.louisvuitton.com', 'msft.it', 'lprk.co', 'split.to', 'deb.li', 'nwsdy.li', 'rebelne.ws', 'yoox.ly', '2doc.net', 'lihi3.cc', 'lohud.us', 'beth.games', 'tbrd.co', 'monster.cat', 'on.mktw.net', 's.g123.jp', 'on.bcg.com', 'smsb.co', 'bst.bz', 'nbcct.co', 'llk.dk', 'dell.to', 'zws.im', 'pag.la', 'db.tt', 'xvirt.it', 'dwz.tax', 'w5n.co', 'viaalto.me', 'selnd.com', 'clck.ru', 'samcart.me', 'buff.ly', 'iii.im', 'snip.ly', 'scuf.co', 'lstu.fr', 'smart.link', 'chng.it', 'c11.kr', 'crackm.ag', 'puext.in', 'lnkd.in', 'dive.pub', 'urla.ru', 'vineland.dj', 'dis.gd', 'risu.io', 'dlvr.it', 'g.asia', 'ynews.page.link', 'swiy.co', 'read.bi', 'shorter.me', 'lihi.one', 'g.co', 'pldthome.info', 'xfru.it', 'vn.rog.gg', 'jp.rog.gg', 'smsng.us', 'btwrdn.com', 'go.lu-h.de', 'warby.me', '1o2.ir', 'url.cy', 'accntu.re', 'kli.cx', 'iplogger.co', 'hyperx.gg', 'bitly.is', 'b23.ru', 'abc7ne.ws', 'engt.co', 'avydn.co', 'pe.ga', 'nvda.ws', 'ilang.in', 'gr.pn', 'e.vg', 'lru.jp', 't-mo.co', 'thesne.ws', 'qvc.co', 'sovrn.co', 'offerup.co', 's.id', 'shorturl.gg', 'kko.to', 'go-link.ru', 'shutr.bz', 'wf0.xin', 'go.gcash.com', 'gofund.me', 'ziadi.co', 'low.es', 'entm.ag', 'is.gd', 'binged.it', 'amex.co', 'tinu.be', 'cisn.co', 'bose.life', 'faturl.com', 'vurl.com', 'vrnda.us', 'wenk.io', 'invent.ge', 'purdue.university', 'adol.us', 'alphab.gr', 'usat.ly', 'sqex.to', 'prbly.us', '2link.cc', 'azc.cc', 'r-7.co', 'lnnk.in', 'vz.to', 'urli.ai', 'supr.cl', 'interc.pt', 'bc.vc', 'iplogger.org', 'lsdl.es', 'amc.film', 'unipapa.co', 'geni.us', 'tabsoft.co', 'nyp.st', 't2m.io', 'dl.gl', 'cup.org', 'csmo.us', 'wa.me', 'abelinc.me', 'credicard.biz', 'viaja.am', 'reline.cc', 'ibit.ly', 'capitalfm.co', 'moovit.me', 'uafly.co', '6.gp', 'dld.bz', '4.ly', 'vd55.com', 'slidesha.re', 'upmchp.us', 'lihi.tv', 'mm.rog.gg', 'smu.gs', 'surl.li', 'xgam.es', '2fear.com', 'sy.to', '2wsb.tv', 'chip.tl', 'urlzs.com', 'ru.rog.gg', 'bnetwhk.com', 's.mj.run', 'pros.is', 'alnk.to', 'e.lilly', 'bwnews.pr', 'ouo.press', 'v.gd', 'mcafee.ly', 'tktwb.tw', 'maac.io', 'huffp.st', 'solsn.se', 'ui8.ru', 'esl.gg', 'iplogger.com', 'go.cwtv.com', 'tek.io', 'baratun.de', 'cockroa.ch', 'rvtv.io', 'l.linklyhq.com', 'ww7.fr', 'fr.rog.gg', 't.me', 'coupa.ng', 'etp.tw', 'dy.fi', 'iea.li', 's.wikicharlie.cl', 'pj.pizza', 'grdt.ai', 'ucbexed.org', 'grb.to', 'roge.rs', 'prf.hn', 'whcs.law', 'fetnet.tw', 'glblctzn.co', 'vi.tc', 'b.link', 'letsharu.cc', 'ja.ma', 'ugp.io', '02faq.com', 'go.nowth.is', 'abc13.co', 'got.to', 'tiny.ee', 'riot.com', 'zipurl.fr', 'bcove.video', 'lmt.co', 'cvs.co', 'goo.su', 'vogue.cm'}
    
def check_is_ip(hostname):
    try:
        ipaddress.ip_address(hostname)
        return 1
    except Exception:
        return 0

def get_whois_record(domain):
    whois_success = 0
    domain_age_days = 0
    creation_year = 0
    print('Perfoming WHOIS lookup...')
    try:
        w = whois.whois(domain)
        res = w.creation_date
        # print(w)
        if isinstance(res, list):
            res = res[0]
        
        if res:
            whois_success = 1
            creation_year = res.year
            
            # Ensure both datetimes are timezone-aware for comparison
            if res.tzinfo is None:
                res = res.replace(tzinfo=timezone.utc)
            
            # Use timezone-aware datetime for comparison
            now = datetime.now(timezone.utc)  # Fixed: now timezone-aware
            domain_age_days = (now - res).days
    except Exception as e:
        print(e)
        whois_success = 0
    
    return {
        'whois_success': whois_success,
        'domain_age_days': domain_age_days,
        'creation_year': creation_year,
    }
            
def extract_all_training_features(url:str):
    try:
        print('Extracting URL features...')
        ext = tldextract.extract(url)
        domain = f'{ext.domain}.{ext.suffix}'
        url_features = urlparse(url)

        entropy(list(Counter(url).values()), base=2)
        
        pattern = r'[^a-zA-Z0-9\s]'

        whois_record = get_whois_record(domain)
        
        features = {
            'whois_success': whois_record['whois_success'],
            'domain_age_days': whois_record['domain_age_days'], 
            'creation_year': whois_record['creation_year'],
        
            # length feature
            'url_length': len(url),
            'domain_length': len(domain),
            'hostname_length': len(url_features.hostname),
            'path_length': len(url_features.path),
            'tld_length': len(ext.suffix),
            'query_length': len(url_features.query),

            # Count features

            'num_digits': sum(c.isdigit() for c in url),
            'num_letters': sum(c.isalpha() for c in url),
            'num_uppercase': sum(1 for char in url if char.isupper()),
            'num_lowercase': sum(1 for char in url if char.islower()),
            'num_subdomains': len(ext.subdomain.split('.')) if ext.subdomain else 0,
            'num_dots': url.count('.'),
            'num_hyphen': url.count('-'),
            'num_at': url.count('@'),
            'num_percent': url.count('%'),
            'num_question': url.count('?'),
            'num_equal': url.count('='),
            'num_hash': url.count('#'),
            'num_ampersand': url.count('&'),
            'num_underscore': url.count('_'),
            'num_dollars': url.count('$'),
            'num_slashes': url.count('/'),
            'num_params': len(url_features.query.split('&')) if url_features.query else 0,

            # entropy features
            'entropy_url' : round(float(entropy(list(Counter(url).values()), base=2)), 2),
            'entropy_path': round(float(entropy(list(Counter(url_features.path).values()), base=2)), 2),
            'entropy_domain': round(float(entropy(list(Counter(domain).values()), base=2)), 2),
            'entropy_query': round(float(entropy(list(Counter(url_features.query).values()), base=2)), 2),

            # ratio features
            'ratio_digits': round(sum(c.isdigit() for c in url) / len(url),2),
            'ratio_letters': round(sum(c.isalpha() for c in url) / len(url),2),
            'ratio_ uppercase': round(sum(1 for char in url if char.isupper())/len(url),2),
            'ratio_lowercase': round(sum(1 for char in url if char.islower())/len(url),2),

            # containment_features
            'contains_login': 1 if any(w in url.lower() for w in ['access','', 'login', 'signin']) else 0,
            'contains_verify': 1 if any(w in url.lower() for w in ['confirm','verify','verification']) else 0,
            'contains_secure': 1 if any(w in url.lower() for w in ['secure', 'safe', 'security']) else 0,
            'contains_update': 1 if any(w in url.lower() for w in ['update', 'upgrade']) else 0,
            'contains_bank': 1 if any(w in url.lower() for w in ['bank', 'secure', 'login', 'signin', 'verify']) else 0,
            'contains_crypto': 1 if any(w in url.lower() for w in ['crypto', 'bit', 'coin', 'eth', 'blockchain']) else 0,
            'contains_pay': 1 if any(w in url.lower() for w in ['paypal', 'pay', 'wallet', 'checkout']) else 0,
            'contains_obfuscation': 1 if any(x in url for x in ['%%', 'hex', 'encoding']) else 0,
            
            #other features
            'has_specials': 1 if re.search(pattern, url) else 0,
            'is_ip_address':check_is_ip(hostname=url_features.hostname),
            'uses_https': 1 if url_features.scheme == 'https' else 0,
            'has_www' : 1 if url_features.hostname and url_features.hostname.startswith('www.') else 0,
            'unusual_double_slash': 1 if url.count("//") > 1 else 0,
            'is_shortened': 1 if domain in MY_SHORTENERS else 0,
        }
        return features
    except Exception as e:
        return e

# extract_all_training_features('https://is.gd:8000/ipfs/qmMsw6iwtrv3yptvhbpmal9vua4ckdceyrw2twl1s6jh2ox?cmd=1&now=true#top')
class EnsemblePredictor:
    def __init__(self, model_paths):
        """Initialize and load all models once"""
        self.models = {}
        for name, path in model_paths.items():
            with open(path, 'rb') as f:
                self.models[name] = joblib.load(f)
        print(f"Loaded {len(self.models)} models")
    
    def _get_prediction(self, name, model, df):
        """Get prediction from a single model, handling different output formats"""
        try:
            pred = model.predict(df)
            
            # Flatten if needed
            if isinstance(pred, np.ndarray):
                pred = pred.flatten()[0]
            
            # Convert probability to class if needed
            if 0 < pred < 1:
                pred = 1 if pred >= 0.5 else 0
            
            return int(pred)
        
        except Exception as e:
            print(f"Error with {name}: {e}")
            return None
    
    def predict(self, features, method='voting', threshold=0.5):
        """Make prediction using loaded models"""
        if isinstance(features, dict):
            df = pd.DataFrame([features])
        else:
            df = features
        
        predictions = []
        final_prediction = {}
        for name, model in self.models.items():
            pred = self._get_prediction(name, model, df)
            if pred is not None:
                predictions.append(pred)
                # final_prediction.update({f'{name}:{pred}'})
                final_prediction[f'{name}'] = pred
                # print(f"{name}: {pred}")
        
        if not predictions:
            raise ValueError("No valid predictions from any model")
        
        if method == 'voting':
            final_prediction['final_verdict'] = max(set(predictions), key=predictions.count)
            # return max(set(predictions), key=predictions.count)
        # elif method == 'all':
        #     return predictions
        # elif method == 'any':
        #     return 1 if 1 in predictions else 0
        
        return final_prediction


# # Usage
# predictor = EnsemblePredictor({
#     'cnn': 'models/cnn_model.joblib',
#     'random_forest': 'models/random_forest_model.joblib',
#     'decision_tree': 'models/decision_tree_model.joblib',
# })

# req_url = input('Enter test url: ')
# features = extract_all_training_features(url=req_url)
# result = predictor.predict(features)
# # print(f"\nFinal Prediction: {result} - {'Phishing' if result == 1 else 'Legitimate'}")
# print(result)