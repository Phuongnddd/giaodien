#include <AccelStepper.h>

// Chân stepper
#define STEP_Y 4  
#define DIR_Y 3   
#define STEP_X 7  
#define DIR_X 6    
#define STEP_Z 10
#define DIR_Z 9

// Công tắc hành trình gốc
#define Y_LIMIT 31  
#define X_LIMIT 30
#define Z_LIMIT 32
#define RELAY_PIN 12

// Điều chỉnh thông số
#define MAGNET_STABILIZE_TIME 2000  // Thời gian chờ nam châm ổn định (ms)
#define LIFTING_SPEED 300           // Tốc độ nâng vật sau khi gắp (giảm xuống)
#define Z_ACCEL_LIFTING 200         // Gia tốc trục Z khi nâng vật (giảm xuống)

AccelStepper stepperY(AccelStepper::DRIVER, STEP_Y, DIR_Y); 
AccelStepper stepperX(AccelStepper::DRIVER, STEP_X, DIR_X);  
AccelStepper stepperZ(AccelStepper::DRIVER, STEP_Z, DIR_Z);

void homeAxes() {
  // Home Y
  stepperY.setSpeed(-200);
  while (digitalRead(Y_LIMIT) == HIGH) {
    stepperY.runSpeed();
  }
  stepperY.setCurrentPosition(0);
  
  // Home X
  stepperX.setSpeed(-1000);
  while (digitalRead(X_LIMIT) == HIGH) {
    stepperX.runSpeed();
  }
  stepperX.setCurrentPosition(0);
  
  // Home Z
  stepperZ.setSpeed(-500);
  while (digitalRead(Z_LIMIT) == HIGH) {
    stepperZ.runSpeed();
  }
  stepperZ.setCurrentPosition(0);
}

void moveXYZ(long x, long y, long z, int relayState = -1) {
  stepperX.moveTo(x);
  stepperY.moveTo(y);
  stepperZ.moveTo(z);
  
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0 || stepperZ.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
    stepperZ.run();
    delay(1);
  }

  if (relayState == 1) {
    digitalWrite(RELAY_PIN, HIGH);
    Serial.println("Nam châm điện đã bật (trong moveXYZ)");
  } else if (relayState == 0) {
    digitalWrite(RELAY_PIN, LOW);
    Serial.println("Nam châm điện đã tắt (trong moveXYZ)");
  }
}

void controlRelay(bool state) {
  digitalWrite(RELAY_PIN, state ? HIGH : LOW);
  Serial.print("Nam châm điện đã ");
  Serial.println(state ? "BẬT" : "TẮT");
}

// Hàm nâng vật với tham số tốc độ và gia tốc tùy chỉnh
void liftWithObject(long x, long y, long z) {
  // Lưu lại tốc độ và gia tốc hiện tại của trục Z
  float currentMaxSpeed = stepperZ.maxSpeed();
  float currentAccel = stepperZ.acceleration();
  
  // Thiết lập tốc độ và gia tốc thấp hơn cho trục Z khi nâng vật
  stepperZ.setMaxSpeed(LIFTING_SPEED);
  stepperZ.setAcceleration(Z_ACCEL_LIFTING);
  
  // Thực hiện di chuyển
  stepperX.moveTo(x);
  stepperY.moveTo(y);
  stepperZ.moveTo(z);
  
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0 || stepperZ.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
    stepperZ.run();
    delay(1);
  }
  
  // Khôi phục tốc độ và gia tốc ban đầu
  stepperZ.setMaxSpeed(currentMaxSpeed);
  stepperZ.setAcceleration(currentAccel);
}

void setup() {
  Serial.begin(9600);
  
  pinMode(Y_LIMIT, INPUT_PULLUP);
  pinMode(X_LIMIT, INPUT_PULLUP);
  pinMode(Z_LIMIT, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Đảm bảo relay tắt khi khởi động
  
  stepperY.setMaxSpeed(200);
  stepperY.setAcceleration(200);
  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(500);
  stepperZ.setMaxSpeed(1000);
  stepperZ.setAcceleration(500);
  
  Serial.println("Robot Control System (Nam châm điện)");
  Serial.println("-------------------------------------");
  Serial.println("Các lệnh có sẵn:");
  Serial.println("HOME - Về vị trí gốc");
  Serial.println("MOVE X Y Z - Di chuyển đến tọa độ");
  Serial.println("RELAY ON/OFF - Điều khiển nam châm điện");
  Serial.println("HOP1 - Thực hiện chu trình gắp vật và thả vật hoàn chỉnh");
  Serial.println("-------------------------------------");
  Serial.println("Homing...");
  homeAxes();
  delay(500);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase(); // Chuyển thành chữ hoa để xử lý nhất quán
    
    Serial.print("Nhận lệnh: ");
    Serial.println(cmd);
    
    if (cmd.startsWith("MOVE ")) {
      // Xử lý lệnh MOVE X Y Z
      String params = cmd.substring(5); // Bỏ "MOVE "
      params.trim();
      
      int firstSpace = params.indexOf(' ');
      int secondSpace = params.indexOf(' ', firstSpace + 1);
      
      if (firstSpace > 0 && secondSpace > 0) {
        long x = params.substring(0, firstSpace).toInt();
        long y = params.substring(firstSpace + 1, secondSpace).toInt();
        long z = params.substring(secondSpace + 1).toInt();
        
        Serial.print("Di chuyển đến (");
        Serial.print(x);
        Serial.print(", ");
        Serial.print(y);
        Serial.print(", ");
        Serial.print(z);
        Serial.println(")");
        
        moveXYZ(x, y, z);
      } else {
        Serial.println("Định dạng sai. Sử dụng: MOVE X Y Z");
      }
    }
    else if (cmd == "HOP1") {
      Serial.println("Thực hiện chu trình gắp và thả vật");
      
      // Di chuyển đến vị trí trên vật
      Serial.println("1. Di chuyển đến vị trí trên vật...");
      moveXYZ(93, 1340, 5000);
      delay(500);
      
      // Hạ xuống gần vật
      Serial.println("2. Hạ xuống gần vật...");
      moveXYZ(93, 1340, 300, 0); // Đảm bảo nam châm đã tắt khi tiếp cận
      delay(500);
      
      // Bật nam châm điện để gắp vật
      Serial.println("3. Bật nam châm điện để gắp vật...");
      controlRelay(true);
      delay(MAGNET_STABILIZE_TIME); // Đợi lâu hơn để đảm bảo nam châm hoạt động tốt
      
      // Nâng vật lên cao với tốc độ chậm hơn
      Serial.println("4. Nâng vật lên cao (tốc độ chậm)...");
      liftWithObject(93, 1340, 1000); // Nâng lên ở vị trí hiện tại với tốc độ chậm
      delay(500);
      
      // Tiếp tục nâng cao hơn
      liftWithObject(93, 1340, 5000);
      delay(500);
      
      // Di chuyển đến vị trí thả
      Serial.println("5. Di chuyển đến vị trí thả...");
      moveXYZ(16000, 831, 5000, 1); // Giữ nam châm bật trong quá trình di chuyển
      delay(500);
      
      // Hạ xuống vị trí thả
      Serial.println("6. Hạ xuống vị trí thả...");
      moveXYZ(16000, 831, 1000, 1); // Giữ nam châm bật khi hạ xuống
      delay(500);
      
      // Tắt nam châm điện để thả vật
      Serial.println("7. Tắt nam châm điện để thả vật...");
      controlRelay(false);
      delay(1000); // Đợi để đảm bảo vật được thả hoàn toàn
      
      // Nâng lên sau khi thả
      Serial.println("8. Nâng lên sau khi thả...");
      moveXYZ(16000, 831, 5000, 0); // Giữ nam châm tắt khi nâng lên
      delay(500);
      
      Serial.println("Hoàn thành chu trình gắp và thả vật!");
    }
    else if (cmd == "HOME") {
      Serial.println("Về vị trí gốc");
      homeAxes();
    }
    else if (cmd == "RELAY ON") {
      controlRelay(true);
    }
    else if (cmd == "RELAY OFF") {
      controlRelay(false);
    }
    else {
      Serial.println("Lệnh không hợp lệ. Vui lòng thử lại.");
    }
  }
  
  stepperX.run();
  stepperY.run();
  stepperZ.run();
}
