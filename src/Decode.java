import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Random;

import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;


public class Decode {
	
	static int month = 9;
	static boolean music = false;
	static String[] urls = new String[12];
	
	public static void main(String[] args) {
		
		urls[10] = "http://decoder.kr/wp-admin/admin-ajax.php?action=ab_render_time&form_id=6142beeadd493&selected_date=2021-10-01&cart_key=0";
		urls[9] = "http://decoder.kr/wp-admin/admin-ajax.php?action=ab_render_time&form_id=6142beeadd493&selected_date=2021-09-01&cart_key=0";
			
		
		while(true) {
			try {
				int random =(int) (Math.random() * 8000);
				Thread.sleep(2000 + random);
			} catch (Exception e) {
				System.err.println(e);
			}
			get();
		}
		
	}
	
	public static void play() {
		new Thread(new Runnable() {
		  // The wrapper thread is unnecessary, unless it blocks on the
		  // Clip finishing; see comments.
		    public void run() {
		    	try {
		    		Path relativePath = Paths.get("");
		    		String path = relativePath.toAbsolutePath().toString();
		    		File file = new File(path + File.separator + "music" + File.separator +  "music.wav");
		    		Clip clip = AudioSystem.getClip(); 
		    		clip.open(AudioSystem.getAudioInputStream(file)); 
		    		// clip.loop(Clip.LOOP_CONTINUOUSLY); 
		    		clip.loop(3); 
		    		clip.start();
		    		System.out.println("START");
		    	} catch (Exception e) {
		    		System.out.println("ERR");
		    		System.err.println(e.getMessage());
		    	}
		    }
	  }).start();
	}
	
	public static void get() {
		try {
			long time = System.currentTimeMillis ();
			System.out.println (time);
			
			String urlStr = urls[month];
			URL url = new URL(urlStr);
			month = month == 9 ? 10 : 9;
//			URL url = new URL("http://decoder.kr/wp-admin/admin-ajax.php?action=ab_render_time&form_id=6123cd45ed969&selected_date=2021-11-01&cart_key=0");
			HttpURLConnection con = (HttpURLConnection) url.openConnection(); 
			con.setConnectTimeout(5000); 
			con.setReadTimeout(5000); 			
			con.setRequestMethod("GET");
			con.setRequestProperty("Cookie", "_ga=GA1.2.2120761759.1629701316; PHPSESSID=p6bmldnov3qdskbmf4j9ar4uh4; _gid=GA1.2.1123263900.1631756359; _gat=1");
			
			
			con.setDoOutput(false); 
			
			StringBuilder sb = new StringBuilder();
			if (con.getResponseCode() == HttpURLConnection.HTTP_OK) {
				BufferedReader br = new BufferedReader(
						new InputStreamReader(con.getInputStream(), "utf-8"));
				String line;
				while ((line = br.readLine()) != null) {
					
					String[] sp = line.split("<button");
					
					for (String string : sp) {
						String target = string.substring(2,10);
						if(target.equals("disabled")) {
							;;
							System.out.println("DISABLE");
						}else if(target.equals("lass=\\\"a")){
							System.out.println(string.substring(36,46));
						}else if(target.equals("success\"")){
							;;
							System.out.println("GET SUCCESS");
						}else {
							System.out.println("ENABLE");
							System.out.println("====================");
							System.out.println("====================");
							System.out.println("====================");
							System.out.println(string);
							System.out.println("====================");
							System.out.println("====================");
							System.out.println("====================");
							if(!music) {
								music = true;
								play();
							}
						}
					}
				}
				br.close();
				System.out.println("" + sb.toString());
				
			} else {
				System.out.println(con.getResponseMessage());
			}
			
		} catch (Exception e) {
			System.out.println("ERROR");
			System.err.println(e.toString());
		}
	}
}



