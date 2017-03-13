//runbrow
import java.io.IOException;

import java.lang.reflect.InvocationTargetException;

import java.lang.reflect.Method;

public class runbrow {
	public static void main(String[] args) throws Exception {
		boolean s=null;
		System.out.println(s);
		String url="http://p.nju.edu.cn";
		Runtime.getRuntime().exec("rundll32 url.dll,FileProtocolHandler " + url);
	}
}