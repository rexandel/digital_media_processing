using System;
using OpenCvSharp;

class Program
{
    static Mat ImagePreprocessing(string path)
    {
        Mat image = Cv2.ImRead(path, ImreadModes.Color);
        Mat grayscale = new Mat();
        Cv2.CvtColor(image, grayscale, ColorConversionCodes.BGR2GRAY);
        Mat grayscaleBlur = new Mat();
        Cv2.GaussianBlur(grayscale, grayscaleBlur, new Size(9, 9), 3);
        return grayscaleBlur;
    }

    static (float[,], float[,]) SobelKernels()
    {
        float[,] Gx = new float[3, 3]
        {
            { -1, 0, 1 },
            { -2, 0, 2 },
            { -1, 0, 1 }
        };

        float[,] Gy = new float[3, 3]
        {
            { -1, -2, -1 },
            {  0,  0,  0 },
            {  1,  2,  1 }
        };

        return (Gx, Gy);
    }

    static (Mat, Mat, Mat) Sobel(Mat img)
    {
        var (Gx, Gy) = SobelKernels();
        int kernelSize = 3;
        int paddingSize = kernelSize / 2;

        Mat imgPadded = new Mat();
        Cv2.CopyMakeBorder(img, imgPadded, paddingSize, paddingSize, paddingSize, paddingSize, BorderTypes.Reflect);

        int height = img.Rows;
        int width = img.Cols;

        Mat gradX = new Mat(height, width, MatType.CV_32FC1, Scalar.All(0));
        Mat gradY = new Mat(height, width, MatType.CV_32FC1, Scalar.All(0));

        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float valX = 0;
                float valY = 0;

                int yPadded = y + paddingSize;
                int xPadded = x + paddingSize;

                for (int k = 0; k < kernelSize; k++)
                {
                    for (int l = 0; l < kernelSize; l++)
                    {
                        byte pixel = imgPadded.At<byte>(yPadded + k - paddingSize, xPadded + l - paddingSize);
                        valX += pixel * Gx[k, l];
                        valY += pixel * Gy[k, l];
                    }
                }

                gradX.Set(y, x, valX);
                gradY.Set(y, x, valY);
            }
        }

        Mat magnitude = new Mat(height, width, MatType.CV_32FC1);
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float gx = gradX.At<float>(y, x);
                float gy = gradY.At<float>(y, x);
                float mag = (float)Math.Sqrt(gx * gx + gy * gy);
                magnitude.Set(y, x, mag);
            }
        }

        Mat magnitudeNormalized = new Mat();
        Cv2.Normalize(magnitude, magnitudeNormalized, 0, 255, NormTypes.MinMax);
        Mat magnitudeU8 = new Mat();
        magnitudeNormalized.ConvertTo(magnitudeU8, MatType.CV_8UC1);

        return (magnitudeU8, gradX, gradY);
    }

    static int AngleNum(float x, float y, float tg)
    {
        if (x >= 0 && y <= 0)
        {
            if (tg < -2.414f)
                return 0;
            else if (tg < -0.414f)
                return 1;
            else
                return 2;
        }
        else if (x >= 0 && y >= 0)
        {
            if (tg < 0.414f)
                return 2;
            else if (tg < 2.414f)
                return 3;
            else
                return 4;
        }
        else if (x <= 0 && y >= 0)
        {
            if (tg < -2.414f)
                return 4;
            else if (tg < -0.414f)
                return 5;
            else
                return 6;
        }
        else if (x <= 0 && y <= 0)
        {
            if (tg < 0.414f)
                return 6;
            else if (tg < 2.414f)
                return 7;
            else
                return 0;
        }
        else
        {
            return 0;
        }
    }

    static Mat NonMaximumSuppression(Mat magnitude, Mat gradX, Mat gradY)
    {
        int height = magnitude.Rows;
        int width = magnitude.Cols;

        Mat tg = new Mat(height, width, MatType.CV_32FC1);
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float gx = gradX.At<float>(y, x);
                float gy = gradY.At<float>(y, x);
                float tangent = (gx != 0) ? gy / gx : (Math.Sign(gy) * float.MaxValue);
                tg.Set(y, x, tangent);
            }
        }

        Mat edges = new Mat(height, width, MatType.CV_8UC1, Scalar.All(0));

        for (int y = 1; y < height - 1; y++)
        {
            for (int x = 1; x < width - 1; x++)
            {
                float gx = gradX.At<float>(y, x);
                float gy = gradY.At<float>(y, x);
                float tangent = tg.At<float>(y, x);
                int angle = AngleNum(gx, gy, tangent);

                int[] neighbor1 = new int[2];
                int[] neighbor2 = new int[2];

                if (angle == 0 || angle == 4)
                {
                    neighbor1[0] = y; neighbor1[1] = x - 1;
                    neighbor2[0] = y; neighbor2[1] = x + 1;
                }
                else if (angle == 1 || angle == 5)
                {
                    neighbor1[0] = y - 1; neighbor1[1] = x + 1;
                    neighbor2[0] = y + 1; neighbor2[1] = x - 1;
                }
                else if (angle == 2 || angle == 6)
                {
                    neighbor1[0] = y - 1; neighbor1[1] = x;
                    neighbor2[0] = y + 1; neighbor2[1] = x;
                }
                else if (angle == 3 || angle == 7)
                {
                    neighbor1[0] = y - 1; neighbor1[1] = x - 1;
                    neighbor2[0] = y + 1; neighbor2[1] = x + 1;
                }
                else
                {
                    neighbor1[0] = y; neighbor1[1] = x;
                    neighbor2[0] = y; neighbor2[1] = x;
                }

                byte currentMag = magnitude.At<byte>(y, x);
                byte mag1 = magnitude.At<byte>(neighbor1[0], neighbor1[1]);
                byte mag2 = magnitude.At<byte>(neighbor2[0], neighbor2[1]);

                if (currentMag >= mag1 && currentMag >= mag2)
                {
                    edges.Set(y, x, currentMag);
                }
            }
        }

        return edges;
    }

    static Mat DoubleThresholdFiltering(Mat edges, Mat magnitude, float lowPercent, float highPercent)
    {
        double minVal, maxVal;
        Cv2.MinMaxLoc(magnitude, out minVal, out maxVal);

        int lowLevel = (int)(maxVal * lowPercent);
        int highLevel = (int)(maxVal * highPercent);

        Mat strongEdges = new Mat();
        Cv2.Threshold(edges, strongEdges, highLevel, 255, ThresholdTypes.Binary);

        Mat weakEdges = new Mat();
        Cv2.InRange(edges, lowLevel, highLevel - 1, weakEdges);

        Mat finalEdges = new Mat(edges.Size(), MatType.CV_8UC1, Scalar.All(0));
        Cv2.BitwiseOr(finalEdges, strongEdges, finalEdges);

        int height = edges.Rows;
        int width = edges.Cols;

        for (int y = 1; y < height - 1; y++)
        {
            for (int x = 1; x < width - 1; x++)
            {
                if (weakEdges.At<byte>(y, x) > 0)
                {
                    bool connected = false;
                    for (int dy = -1; dy <= 1 && !connected; dy++)
                    {
                        for (int dx = -1; dx <= 1 && !connected; dx++)
                        {
                            if (dy == 0 && dx == 0)
                                continue;

                            int ny = y + dy;
                            int nx = x + dx;

                            if (ny >= 0 && ny < height && nx >= 0 && nx < width)
                            {
                                if (strongEdges.At<byte>(ny, nx) > 0)
                                {
                                    finalEdges.Set(y, x, 255);
                                    connected = true;
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }

        return finalEdges;
    }

    static Mat CannyEdgeDetector(string path, float lowPercent, float highPercent)
    {
        Mat imgPreprocessed = ImagePreprocessing(path);
        var (magnitude, gradX, gradY) = Sobel(imgPreprocessed);

        Mat nmsEdges = NonMaximumSuppression(magnitude, gradX, gradY);
        Mat finalEdges = DoubleThresholdFiltering(nmsEdges, magnitude, lowPercent, highPercent);

        return finalEdges;
    }

    static void Main()
    {
        string path = @"D:\GitHub\digital_media_processing\canny_edge_detector\images\flower.jpg";

        float lowPercent = 0.1f;
        float highPercent = 0.3f;

        Mat imgPreprocessed = ImagePreprocessing(path);
        var (magnitude, _, _) = Sobel(imgPreprocessed);

        Mat homemadeCanny = CannyEdgeDetector(path, lowPercent, highPercent);
        Mat opencvCanny = new Mat();
        Cv2.Canny(imgPreprocessed, opencvCanny, 50, 150);

        Cv2.NamedWindow("Preprocessed Image", WindowFlags.Normal);
        Cv2.NamedWindow("Sobel Magnitude", WindowFlags.Normal);
        Cv2.NamedWindow("Homemade Canny", WindowFlags.Normal);
        Cv2.NamedWindow("OpenCV Canny", WindowFlags.Normal);

        Cv2.ImShow("Preprocessed Image", imgPreprocessed);
        Cv2.ImShow("Sobel Magnitude", magnitude);
        Cv2.ImShow("Homemade Canny", homemadeCanny);
        Cv2.ImShow("OpenCV Canny", opencvCanny);

        Cv2.WaitKey(0);
        Cv2.DestroyAllWindows();
    }
}