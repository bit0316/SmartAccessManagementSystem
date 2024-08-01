package com.yu.smartaccessmanagementsystem;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private static final String SERVER_IP = "192.168.46.196";
    private static final int SERVER_PORT = 9999;

    private InputStream in;
    private Button connectButton;
    private Button checkButton;
    private Button openButton;
    private Button onButton;
    private ImageView imageView;
    private TextView messageTextView;
    private TextView responseTextView;
    private Socket socket;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        connectButton = findViewById(R.id.connectButton);
        checkButton = findViewById(R.id.checkButton);
        openButton = findViewById(R.id.openButton);
        messageTextView = findViewById(R.id.messageTextView);
        imageView = findViewById(R.id.imageView);
        onButton = findViewById(R.id.onButton);
        responseTextView = findViewById(R.id.responseTextView);
        messageTextView.setFocusableInTouchMode(true);

        connectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ConnectTask connectTask = new ConnectTask();
                connectTask.execute();
            }
        });

        checkButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ConnectTask connectTask = new ConnectTask();
                connectTask.execute();
                if (socket != null && socket.isConnected()) {
                    sendCommand("check");
                    sendCommand("user_id");
                    sendCommand("21912254");
                }
            }
        });

        openButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (socket != null && socket.isConnected()) {
                    sendCommand("open");
                }
            }
        });

        onButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ConnectTask connectTask = new ConnectTask();
                connectTask.execute();
                if (socket != null && socket.isConnected()) {
                    sendCommand("condition");
                    readListData();
                }
            }
        });

        messageTextView.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
                if (actionId == EditorInfo.IME_ACTION_DONE || (event != null && event.getKeyCode() == KeyEvent.KEYCODE_ENTER && event.getAction() == KeyEvent.ACTION_DOWN)) {
                    String message = messageTextView.getText().toString();
                    if (socket != null && socket.isConnected()) {
                        sendCommand("user_id");
                        sendCommand("21912254");
                    }
                    return true;
                }
                return false;
            }
        });

    }

    private class ConnectTask extends AsyncTask<Void, String, Bitmap> {
        private OutputStream out;
        private byte[] receivedImageData;
        private Bitmap decodedBitmap;
        private String receivedData;

        @Override
        protected Bitmap doInBackground(Void... voids) {
            try {
                socket = new Socket(SERVER_IP, SERVER_PORT);
                in = socket.getInputStream();
                out = socket.getOutputStream();
                while (true) {
                    // 이미지 데이터 크기 수신
                    byte[] sizeBuffer = new byte[4];
                    int sizeBytesRead = in.read(sizeBuffer);
                    if (sizeBytesRead != -1) {
                        int imageSize = ByteBuffer.wrap(sizeBuffer).getInt();
                        Log.d("Image", "Image size: " + imageSize);

                        // 이미지 데이터 수신
                        receivedImageData = new byte[imageSize];
                        int totalBytesRead = 0;
                        while (totalBytesRead < imageSize) {
                            int bytesRead = in.read(receivedImageData, totalBytesRead, imageSize - totalBytesRead);
                            if (bytesRead == -1) {
                                break;
                            }
                            totalBytesRead += bytesRead;
                        }

                        if (totalBytesRead != imageSize) {
                            throw new IOException("Failed to receive complete image data.");
                        }
                        Log.d("Image", "Total bytes read: " + totalBytesRead);

                        // Check if the received data represents image data
                        boolean isImageData = isImageData(receivedImageData);

                        // 수신된 이미지 데이터 처리
                        if (isImageData) {

                            // 수신된 이미지 데이터 처리
                            Bitmap receivedBitmap = BitmapFactory.decodeByteArray(receivedImageData, 0, receivedImageData.length);

                            return receivedBitmap;
                        }
                        // 문자열 데이터 수신 처리
                        else {
                            receivedData = new String(receivedImageData);
                            if (receivedData.equals("warning")) {
                                // 경고 메시지를 수신했을 때 알림 팝업 생성
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        AlertDialog.Builder builder = new AlertDialog.Builder(MainActivity.this);
                                        builder.setTitle("경고")
                                                .setMessage("경고 메시지를 수신했습니다.")
                                                .setPositiveButton("확인", null)
                                                .show();
                                    }
                                });
                            } else {
                                // 수신한 문자열 데이터 처리
                                publishProgress(receivedData);
                            }
                        }
                        // 이미지 데이터를 모두 수신했으므로 반복문 종료
                        break;
                    } else {
                        break; // 데이터 수신이 종료되었으므로 반복문 종료
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
                showToast("오류가 발생했습니다: " + e.getMessage());
            }

            return null;
        }

        // 이미지 데이터 수신 여부 확인
        private boolean isImageData(byte[] data) {
            // 이미지 파일 시그니처(signature) 배열 (JPEG, PNG, GIF, BMP 등의 시그니처)
            byte[] jpegSignature = {(byte) 0xFF, (byte) 0xD8};
            byte[] pngSignature = {(byte) 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A};
            byte[] gifSignature = {'G', 'I', 'F'};
            byte[] bmpSignature = {'B', 'M'};

            // 주어진 데이터와 각 이미지 파일 시그니처를 비교하여 이미지인지 확인
            if (startsWith(data, jpegSignature) || startsWith(data, pngSignature) || startsWith(data, gifSignature) || startsWith(data, bmpSignature)) {
                return true;
            }

            // 비이미지 데이터인 경우 false 반환
            return false;
        }

        // 주어진 배열의 시작 부분이 주어진 시그니처와 일치하는지 확인하는 유틸리티 메서드
        private boolean startsWith(byte[] data, byte[] signature) {
            if (data.length < signature.length) {
                return false;
            }

            for (int i = 0; i < signature.length; i++) {
                if (data[i] != signature[i]) {
                    return false;
                }
            }

            return true;
        }

        @Override
        protected void onProgressUpdate(String... values) {
            // 문자열 데이터를 받은 경우 UI 스레드에서 처리하여 responseTextView에 표시
            String receivedData = values[0];
            responseTextView.setText(receivedData);
        }

        @Override
        protected void onPostExecute(Bitmap receivedBitmap) {
            super.onPostExecute(receivedBitmap);
            if (receivedBitmap != null) {
                // 이미지를 받은 경우, imageView에 비트맵 설정
                imageView.setImageBitmap(receivedBitmap);
            } else {
                // 이미지를 받지 못한 경우, 비트맵이 null인 경우에는 responseTextView에 데이터 표시
                if (decodedBitmap != null) {
                    // 이미지뷰에 디코딩된 비트맵 설정
                    imageView.setImageBitmap(decodedBitmap);
                } else {
                    responseTextView.setText(receivedData);
                }
            }
        }
    }

    // 두 개의 비트맵을 합치는 메서드
    private Bitmap mergeBitmaps(Bitmap firstBitmap, Bitmap secondBitmap) {
        int maxWidth = Math.max(firstBitmap.getWidth(), secondBitmap.getWidth());
        int maxHeight = Math.max(firstBitmap.getHeight(), secondBitmap.getHeight());

        Bitmap mergedBitmap = Bitmap.createBitmap(maxWidth, maxHeight, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(mergedBitmap);

        int offsetX = (maxWidth - firstBitmap.getWidth()) / 2;
        int offsetY = (maxHeight - firstBitmap.getHeight()) / 2;

        canvas.drawBitmap(firstBitmap, offsetX, offsetY, null);
        canvas.drawBitmap(secondBitmap, offsetX, offsetY, null);

        return mergedBitmap;
    }

    private void showToast(final String message) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show();
            }
        });
    }

    // 수신한 데이터 읽고 출력하는 메서드
    private void readData() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    byte[] buffer = new byte[1024];
                    int bytesRead = -1; // Initialize bytesRead to -1
                    bytesRead = in.read(buffer);
                    if (bytesRead != -1) {
                        String receivedData = new String(buffer, 0, bytesRead);
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                responseTextView.setText(receivedData);
                            }
                        });
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    private void readListData() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    byte[] buffer = new byte[1024];
                    int bytesRead = in.read(buffer);
                    if (bytesRead != -1) {
                        List<String> dataList = parseData(buffer, bytesRead);
                        displayData(dataList);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    private List<String> parseData(byte[] buffer, int bytesRead) {
        // 여기에서 buffer를 파싱하여 리스트로 변환하는 로직을 작성합니다.
        // 예시로 각 줄을 요소로 하는 리스트로 변환합니다.
        String receivedData = new String(buffer, 0, bytesRead);
        String[] lines = receivedData.split("\n");
        
        return Arrays.asList(lines);
    }

    private void displayData(List<String> dataList) {
        StringBuilder sb = new StringBuilder();
        for (String data : dataList) {
            String[] values = data.split(",");
            if (values.length == 5) {
                float pm2p5 = Float.parseFloat(values[0]);
                float pm10 = Float.parseFloat(values[1]);
                float humidity = Float.parseFloat(values[2]);
                float temperature = Float.parseFloat(values[3]);
                int analog_value = Integer.parseInt(values[4]);

                boolean flame = false;
                if (analog_value < 100) {
                    flame = true;
                } else {
                    flame = false;
                }

                // 센서값 출력
                sb.append(String.format(" PM 2.5   %20d ㎍/㎥\n", pm2p5));
                sb.append(String.format(" PM 10    %20d ㎍/㎥\n", pm10));
                sb.append(String.format(" 습도      %25.1f %%\n", humidity));
                sb.append(String.format(" 온도      %25.1f °C\n", temperature));
                sb.append(String.format(" 화재 감지  %22b \n", flame));
            }
        }
        String receivedData = sb.toString();

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                responseTextView.setText(receivedData);
            }
        });
    }

    private void sendCommand(final String command) {
        if (socket != null) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    try {
                        OutputStream out = socket.getOutputStream();
                        PrintWriter writer = new PrintWriter(out, true);
                        writer.println(command);  // 개행 문자를 자동으로 추가해주는 println() 사용
                        writer.flush();  // 버퍼의 데이터를 강제로 전송
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }).start();
        }
    }
}
