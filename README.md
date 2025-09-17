# Fluppy Bird

Trò chơi Flappy Bird mini viết bằng Python và Pygame, sử dụng bộ asset trong thư mục `assets/FluffyBirds-Free-Ver` cùng các hiệu ứng âm thanh ở `assets/sounds`.

## Yêu cầu

- Python 3.9 trở lên
- Phụ thuộc: xem `requirements.txt`

Tùy chọn nhưng khuyến nghị:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cách chạy

```bash
python3 game.py
```

### macOS (Terminal dùng Bash)

```bash
/bin/bash -lc 'cd /Users/xuanhaj/Dev/game/RIaloFLuppy && source .venv/bin/activate && python3 game.py'
```

## Điều khiển

- Nhấn `Space`, `↑` hoặc click chuột trái để vỗ cánh.
- Khi thua, nhấn `Space` để chơi lại.

## Đặc điểm chính

- Parallax background với bầu trời, mây, hàng cây và toà nhà từ bộ asset gốc.
- 04 biến thể thân cây (`Logs.png`) được chọn ngẫu nhiên cho mỗi cặp ống trên/dưới.
- Chim sử dụng 3 frame động và 1 frame thua từ `Red_Bird.png` (thứ tự: thua → cánh ngang → cánh hạ → cánh hạ sâu).
- Âm thanh vỗ cánh, đạt điểm và va chạm lấy từ thư mục `assets/sounds`.
- Hiển thị điểm hiện tại, kỷ lục và gợi ý điều khiển trực tiếp trên màn hình.

## Tuỳ chỉnh gameplay nhanh

Các hằng số chính nằm đầu file `game.py`:

- `PIPE_SPEED`, `PIPE_GAP`, `PIPE_SPAWN_MS`: điều chỉnh tốc độ, khoảng cách, nhịp sinh ống.
- `GRAVITY`, `FLAP_VELOCITY`, `MAX_DROP_SPEED`: cân bằng cảm giác bay.
- `SCREEN_WIDTH`, `SCREEN_HEIGHT`: kích thước cửa sổ game.

Chỉnh sửa giá trị và chạy lại `game.py` để áp dụng.

## Cấu trúc thư mục

```
assets/
  FluffyBirds-Free-Ver/
    Buildings.png
    Clouds.png
    Grass.png
    Logs.png
    Red_Bird.png
    Sky.png
    Trees.png
  sounds/
    sfx_die.wav
    sfx_hit.wav
    sfx_point.wav
    sfx_swooshing.wav
    sfx_wing.wav
game.py
```

Bạn có thể thêm font hoặc biến thể asset khác, chỉ cần cập nhật đường dẫn trong `game.py` nếu đổi tên.
