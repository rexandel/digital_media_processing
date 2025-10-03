#include <opencv2/opencv.hpp>
#include <vector>
#include <cmath>
#include <iostream>

double gauss(int x, int y, double sigma, int a, int b) {
    double two_sigma_squared = 2 * sigma * sigma;
    double exponent = -((x - a) * (x - a) + (y - b) * (y - b)) / two_sigma_squared;
    return std::exp(exponent) / (3.14 * two_sigma_squared);
}

std::vector<std::vector<double>> generate_kernel(int kernel_size, double std_deviation) {
    std::vector<std::vector<double>> kernel(kernel_size, std::vector<double>(kernel_size, 0.0));
    int a = kernel_size / 2;
    int b = kernel_size / 2;

    double sum = 0.0;

    for (int y = 0; y < kernel_size; y++) {
        for (int x = 0; x < kernel_size; x++) {
            kernel[y][x] = gauss(x, y, std_deviation, a, b);
            sum += kernel[y][x];
        }
    }

    for (int y = 0; y < kernel_size; y++) {
        for (int x = 0; x < kernel_size; x++) {
            kernel[y][x] /= sum;
        }
    }

    return kernel;
}

cv::Mat gaussian_blur(const cv::Mat& img, int kernel_size, double std_deviation) {
    std::vector<std::vector<double>> kernel = generate_kernel(kernel_size, std_deviation);

    int padding_size = kernel_size / 2;
    cv::Mat img_padded;
    cv::copyMakeBorder(img, img_padded, padding_size, padding_size, padding_size, padding_size, cv::BORDER_REFLECT);

    cv::Mat blurred = img.clone();
    int height = img.rows;
    int width = img.cols;

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            double val = 0.0;
            int y_padded = y + padding_size;
            int x_padded = x + padding_size;

            for (int k = 0; k < kernel_size; k++) {
                for (int l = 0; l < kernel_size; l++) {
                    val += img_padded.at<uchar>(y_padded + k - padding_size, x_padded + l - padding_size) * kernel[k][l];
                }
            }

            blurred.at<uchar>(y, x) = static_cast<uchar>(std::round(val));
        }
    }

    return blurred;
}

int main() {
    // Disabling OpenCV logging
    cv::utils::logging::setLogLevel(cv::utils::logging::LOG_LEVEL_ERROR);

    int kernel_size = 19;
    double std_deviation = 3.0;

    cv::Mat img = cv::imread(R"(C:\Users\rexandel\Documents\GitHub\digital_media_processing\filtering_and_blurring_methods\images\cat.png)");
    if (img.empty()) {
        std::cerr << "Error: Could not load image" << std::endl;
        return -1;
    }

    cv::Mat img_gray;
    cv::cvtColor(img, img_gray, cv::COLOR_BGR2GRAY);

    if (kernel_size % 2 == 0) {
        std::cerr << "Size of kernel matrix must be odd. Program will terminate with an error" << std::endl;
        return 1;
    }

    cv::Mat img_blur = gaussian_blur(img_gray, kernel_size, std_deviation);

    cv::imshow("Original", img);
    cv::imshow("Gaussian Blur", img_blur);
    cv::waitKey(0);
    cv::destroyAllWindows();

    return 0;
}