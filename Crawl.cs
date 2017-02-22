using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

namespace WebTest
{
    class Crawl
    {
        public static int bb = 0;
        int mark = 0;
        Queue<siteChecked> crawlQueue = new Queue<siteChecked>();
        Queue<siteChecked> crawledQue = new Queue<siteChecked>();
        HashSet<string> crawled = new HashSet<string>();
        List<Task<bool>> tasks = new List<Task<bool>>();
        int levelLimit;
        public class siteChecked
        {
            private siteChecked parent;
            private string url;
            private string hostName;
            private string title;
            //Unused:尚未爬取
            private HttpStatusCode correctCode= HttpStatusCode.Unused;
            //success:未遇到任何错误
            private WebExceptionStatus errorCode = WebExceptionStatus.Success;
            private int level;
            private HashSet<siteChecked> children=new HashSet<siteChecked>();
            public siteChecked(string url,int level,siteChecked parent)
            {
                this.url = url;
                this.level = level;
                this.parent = parent;
            }
            public string getUrl() { return url; }
            public string getTitle() { return title; }
            public void setTitle(string title) { this.title = title; }
            public int getLevel() { return level; }
            public void setCorrectCode(HttpStatusCode code) { this.correctCode = code; }
            public void setErrorCode(WebExceptionStatus code) { this.errorCode = code; }
            public HttpStatusCode getCorrectCode() { return correctCode; }
            public WebExceptionStatus getErrorCode() { return errorCode; }
            public string getHost() { return hostName; }
            public void setHost(string hostName) { this.hostName = hostName; }
            public int getChildCount() { return this.children.Count; }
            public void addorSetChild(siteChecked child)
            {
                if (child != null) children.Add(child);
            }
            public HashSet<siteChecked> getChildren() { return children; }
        }
        private Encoding analyzedCode(HttpWebResponse resp)
        {
            string type = getCharset(resp.ContentType);
            if (type == "") type = getCharset(resp.Headers["Content-Type"]);
            if (type != "") return Encoding.GetEncoding(type);
            else return null;
        }
        private string getCharset(string type)
        {
            if (type == null || type == "") return "";
            string[] strA = type.ToLower().Split(new char[] { ';', '=', ' ' });
            bool flag = false;
            foreach(string s in strA)
            {
                if (s == "charset")
                    flag = true;
                else if (flag) return s;
            }
            return "";
        }
        private byte[] getContentByte(Stream resp)
        {
            ArrayList buffArray = new ArrayList();
            int offset = 1024;
            byte[] buff = new byte[offset];
            int size = resp.Read(buff, 0, offset);
            while(size>0)
            {
                foreach (byte b in buff)
                    buffArray.Add(b);
                size = resp.Read(buff, 0, offset);
            }
            return (byte[]) buffArray.ToArray(typeof(byte));
        }
        public string downloadhtml(siteChecked site)
        {
            string url = site.getUrl();
            if (url == null || url.Length == 0) return "";
            string htmlDecoded="";
            try
            {
                HttpWebRequest req = WebRequest.Create(url) as HttpWebRequest;
                req.UserAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0";
                req.Credentials = CredentialCache.DefaultNetworkCredentials;
                HttpWebResponse resp = req.GetResponse() as HttpWebResponse;
                site.setHost(req.Headers["Host"]);
                site.setCorrectCode(resp.StatusCode);
                Stream respStream = resp.GetResponseStream();
                Encoding code = analyzedCode(resp);
                if(code != null)
                {
                    StreamReader sr = new StreamReader(respStream, code);
                    htmlDecoded = sr.ReadToEnd();
                    sr.Close();
                }
                else
                {
                    byte[] htmlByte = getContentByte(respStream);
                    //用utf-8来解析head里的meta以获取charset（手动分析）
                    string htmlForMeta = Encoding.GetEncoding("utf-8").GetString(htmlByte);
                    string meta_charset = "(<meta[^>]*charset=(['\"]|)(?<charset>[^>\"']*)[\\s\\S]*?>)|(xml[^>]*encoding=('|\")(?<charset>[^>\"']*)[\\S\\s]*?>)";
                    Regex reg = new Regex(meta_charset, RegexOptions.IgnoreCase);
                    Match m = reg.Match(htmlForMeta);
                    string codeType = (m.Captures.Count != 0) ? m.Result("${charset}") : "";
                    if (codeType == "")
                    {
                        //*非标准,此处指无charset
                        site.setCorrectCode(HttpStatusCode.NoContent);
                        htmlDecoded = null;
                    }
                    else htmlDecoded = Encoding.GetEncoding(codeType).GetString(htmlByte);
                }
                resp.Close();
            }
            catch (UriFormatException e)
            {
                //*非标准，指无效url
                site.setErrorCode(WebExceptionStatus.UnknownError);
                htmlDecoded = null;
            }
            catch (WebException ee)
            {
                site.setErrorCode(ee.Status);
                htmlDecoded = null;
            }
            return htmlDecoded;
        }
        public HashSet<string> parseForUrl(string host,string html)
        {
            string hostName = "https://" + host;
            HashSet<string> result = new HashSet<string>();
            Regex TagA = new Regex("(<a[^>]+href=(\"|')(?<url>[^>\"']+)[\\s\\S]*?>)",RegexOptions.IgnoreCase);
            Regex start = new Regex("^http[s]{0,1}://");
            MatchCollection M = TagA.Matches(html);
            foreach(Match m in M)
            {
                string originalUrl = m.Groups["url"].Value;
                Match absolute = start.Match(originalUrl);
                if (absolute.Success)
                    result.Add(originalUrl);
                else if (originalUrl.StartsWith("/") && originalUrl.Length>1)
                {
                    originalUrl = hostName + originalUrl;
                    result.Add(originalUrl);
                }
            }
            return result;
        }
        public void urlQueue(siteChecked head,string html)
        {
            HashSet<string> result;
            result = parseForUrl(head.getHost(),html);
            foreach (string site in result)
            {
                if (!crawled.Contains(site))
                {
                    siteChecked newSite = new siteChecked(site, head.getLevel() + 1, head);
                    head.addorSetChild(newSite);
                    crawlQueue.Enqueue(newSite);
                }
            }
        }
        private void dequeue()
        {
            siteChecked tmp = crawlQueue.Dequeue();
            crawledQue.Enqueue(tmp);
        }
        private void getTitle(siteChecked site,string html)
        {
            Regex rt = new Regex("<title[^>]*?>(?<title>.*)</title>");
            Match m = rt.Match(html);
            if (m.Success)
                site.setTitle(m.Groups["title"].Value);
            else site.setTitle("");
        }
        public bool startBaseFirst()
        {
            mark++;
            siteChecked head;
            head = crawlQueue.First<siteChecked>();
            dequeue();
            Console.WriteLine(head.getUrl() + "下载");
            string baseUrl = head.getUrl();
            string html = downloadhtml(head);
            crawled.Add(baseUrl);
            if (html != null && html != "")
            {
                getTitle(head, html);
                urlQueue(head, html);
                return true;
            }
            else return false;
        }
        public bool startBaseLock()
        {
            mark++;
            siteChecked head;
            lock (crawlQueue)
            {
                head = crawlQueue.First<siteChecked>();
                dequeue();
                Console.WriteLine(head.getUrl()+"下载");
            }
            string baseUrl = head.getUrl();
            string html="";
            try
            {
                html = downloadhtml(head);
            }
            catch(AggregateException e)
            {
                Console.WriteLine(e.InnerException);
                return false;
            }
            crawled.Add(baseUrl);
            if (html != null && html != "")
            {
                getTitle(head, html);
                urlQueue(head, html);
                return true;
            }
            else return false;
        }
        public void startCrawl()
        {
            startBaseFirst();
            //if(crawlQueue.Count != 0)
            while (mark <= 110)
            {
                Task<bool> task = Task.Run(() => startBaseLock());
                tasks.Add(task);
                Thread.Sleep(500);
            }
            Task<bool>[] group = tasks.ToArray();
            Task.WaitAll(group);
            for(int i=0;i<group.Length;i++)
            {
                Console.WriteLine(group[i].Result);
            }
        }
        public siteChecked showBase()
        {
            siteChecked site = crawledQue.Dequeue();
            StreamWriter sr = new StreamWriter(new FileStream("statusShow.txt", FileMode.Append), Encoding.Default);
            Console.WriteLine();
            Console.WriteLine("CrawledUrl: " + site.getUrl());
            Console.WriteLine("Title: " + site.getTitle());
            Console.WriteLine("Host: " + site.getHost());
            Console.WriteLine("Level: " + site.getLevel());
            Console.WriteLine("CorrectCode: " + site.getCorrectCode());
            Console.WriteLine("ErrorCode: " + site.getErrorCode());
            Console.WriteLine("ChildSite: " + site.getChildCount());
            sr.WriteLine();
            sr.WriteLine("CrawledUrl: " + site.getUrl());
            sr.WriteLine("Title: " + site.getTitle());
            sr.WriteLine("Host: " + site.getHost());
            sr.WriteLine("Level: " + site.getLevel());
            sr.WriteLine("CorrectCode: " + site.getCorrectCode());
            sr.WriteLine("ErrorCode: " + site.getErrorCode());
            sr.WriteLine("ChildSite: " + site.getChildCount());
            sr.Close();
            return site;
        }
        public void crawledResultShow()
        {
            siteChecked site=showBase();
            saveData(site);
            while(crawledQue.Count != 0)
            {
                showBase();
            }
            Console.WriteLine("\n" + mark);
        }
        public void saveData(siteChecked site)
        {
            HashSet<siteChecked> children = site.getChildren(); string name = site.getTitle();
            if (name == null || name.Length == 0) name = "temp";
            if (children.Count != 0)
            {
                StreamWriter result = new StreamWriter(new FileStream(name, FileMode.Create), Encoding.Default);
                result.WriteLine("Url: " + site.getUrl());
                foreach (siteChecked child in children)
                {
                    result.WriteLine(child.getCorrectCode() + "\t" + child.getErrorCode());
                }
                result.Close();
            }
        }
        static void Main(string[] args)
        {
            string baseUrl = @"https://www.qunar.com/";
            Crawl crawl = new Crawl();
            crawl.levelLimit = 1;
            siteChecked first = new siteChecked(baseUrl,0,null);
            crawl.crawlQueue.Enqueue(first);
            crawl.startCrawl();
            crawl.crawledResultShow();
        }
    }
}
