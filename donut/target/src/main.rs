use std::io::{self, Write};
use std::thread;
use std::time::{Duration, Instant};

const WIDTH: usize = 80;
const HEIGHT: usize = 22;
const BUFFER_SIZE: usize = WIDTH * HEIGHT;
const LUMINANCE: &[u8] = b".,-~:;=!*#$@";

fn main() {
    let mut angle1: f64 = 0.0;
    let mut angle2: f64 = 0.0;
    let mut pixels = [b' '; BUFFER_SIZE];
    let mut z_buffer = [0.0f64; BUFFER_SIZE];

    let stdout = io::stdout();
    let mut out = stdout.lock();

    write!(out, "\x1b[2J").unwrap();

    let frame_duration = Duration::from_secs_f64(110.0 / 1000.0);

    loop {
        let frame_start = Instant::now();

        pixels.fill(b' ');
        z_buffer.fill(0.0);

        let sin_a1 = angle1.sin();
        let cos_a1 = angle1.cos();
        let sin_a2 = angle2.sin();
        let cos_a2 = angle2.cos();

        for j in (0..628).step_by(7) {
            let theta = j as f64 / 100.0;
            let sin_theta = theta.sin();
            let cos_theta = theta.cos();
            let height = cos_theta + 2.0;

            for i in (0..628).step_by(2) {
                let phi = i as f64 / 100.0;
                let sin_phi = phi.sin();
                let cos_phi = phi.cos();

                let distance =
                    1.0 / (sin_phi * height * sin_a1 + sin_theta * cos_a1 + 5.0);

                let sin_height = sin_phi * height * cos_a1 - sin_theta * sin_a1;

                let x = (40.0
                    + 30.0
                        * distance
                        * (cos_phi * height * cos_a2 - sin_height * sin_a2))
                    as i32;
                let y = (12.0
                    + 15.0
                        * distance
                        * (cos_phi * height * sin_a2 + sin_height * cos_a2))
                    as i32;

                if x < 0 || x >= WIDTH as i32 || y < 0 || y >= HEIGHT as i32 {
                    continue;
                }

                let index = (x + WIDTH as i32 * y) as usize;
                if distance <= z_buffer[index] {
                    continue;
                }

                let luminance = ((sin_theta * sin_a1
                    - sin_phi * cos_theta * cos_a1)
                    * cos_a2
                    - sin_phi * cos_theta * sin_a1
                    - sin_theta * cos_a1
                    - cos_phi * cos_theta * sin_a2)
                    * 8.0;

                let brightness = luminance as isize;
                let ch = LUMINANCE[brightness.max(0) as usize];

                z_buffer[index] = distance;
                pixels[index] = ch;
            }
        }

        write!(out, "\x1b[H").unwrap();
        out.write_all(&pixels).unwrap();
        out.flush().unwrap();

        angle1 += 0.30;
        angle2 += 0.15;

        let elapsed = frame_start.elapsed();
        if elapsed < frame_duration {
            thread::sleep(frame_duration - elapsed);
        }
    }
}
