use std::{thread, time::Duration};
use rand::Rng;

fn main() {
    let matrix_chars = vec![
        "- ", "* ", "% ", "& ", "# ", "@ ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 ", "0 ",
        "ア", "ィ", "イ", "ゥ", "ウ", "ェ", "エ", "ォ", "オ", "カ", "ガ", "キ", "ギ", "ク", "グ", "ケ", "ゲ", "コ",
        "ゴ", "サ", "ザ", "シ", "ジ", "ス", "ズ", "セ", "ゼ", "ソ", "ゾ", "タ", "ダ", "チ", "ヂ", "ッ", "ツ", "ヅ", "テ",
    ];

    let terminal_colors = vec!["22", "28"];
    let screen_width = 150;
    let line_count = 750;
    let line_speed = 0.1;

    let mut line_array = vec![1; screen_width];
    let mut rng = rand::thread_rng();

    for _ in 0..line_count {
        let mut line = String::new();

        for i in 0..screen_width {
            let n = line_array[i];
            if n == 1 || n == 2 {
                if n == 2 {
                    line.push_str("\x1b[38;5;15m");
                    let idx = rng.gen_range(0..matrix_chars.len());
                    line.push_str(matrix_chars[idx]);
                    line_array[i] = 1;
                } else {
                    let color_idx = rng.gen_range(0..terminal_colors.len());
                    line.push_str("\x1b[38;5;");
                    line.push_str(terminal_colors[color_idx]);
                    line.push('m');
                    let idx = rng.gen_range(0..matrix_chars.len());
                    line.push_str(matrix_chars[idx]);
                }

                if rng.gen_range(1..=30) == 1 {
                    line_array[i] = 0;
                }
            } else {
                let color_idx = rng.gen_range(0..terminal_colors.len());
                line.push_str("\x1b[38;5;");
                line.push_str(terminal_colors[color_idx]);
                line.push_str("m ");
                if rng.gen_range(1..=60) == 1 {
                    line_array[i] = 2;
                }
            }
        }

        println!("{}", line);
        thread::sleep(Duration::from_secs_f64(line_speed));
    }
}
