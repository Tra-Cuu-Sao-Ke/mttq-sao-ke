<p align="center">
 <!-- <img width="100px" src="https://res.cloudinary.com/anuraghazra/image/upload/v1594908242/logo_ccswme.svg" align="center" alt="GitHub Readme Stats" /> -->
 <h2 align="center">Bộ Dữ Liệu Sao Kê Từ Thiện Của Mặt Trận Tổ Quốc Việt Nam<br />(Charity Account Statement Dataset of the Vietnam Fatherland Front)</h2>
</p>
  <p align="center">
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/actions">
      <!-- <img alt="Tests Passing" src="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/workflows/Test/badge.svg" /> -->
    </a>
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/graphs/contributors">
      <img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/Tra-Cuu-Sao-Ke/mttq-sao-ke" />
    </a>
    <a href="https://codecov.io/gh/Tra-Cuu-Sao-Ke/mttq-sao-ke">
      <img alt="Tests Coverage" src="https://codecov.io/gh/Tra-Cuu-Sao-Ke/mttq-sao-ke/branch/master/graph/badge.svg" />
    </a>
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/issues">
      <img alt="Issues" src="https://img.shields.io/github/issues/Tra-Cuu-Sao-Ke/mttq-sao-ke?color=0088ff" />
    </a>
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/pulls">
      <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/Tra-Cuu-Sao-Ke/mttq-sao-ke?color=0088ff" />
    </a>
    <a href="https://securityscorecards.dev/viewer/?uri=github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke">
      <img alt="OpenSSF Scorecard" src="https://api.securityscorecards.dev/projects/github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/badge" />
    </a>
  </p>

  <p align="center">
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/issues/new?assignees=&labels=bug&projects=&template=bug_report.yml">Report Bug</a>
    ·
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/issues/new?assignees=&labels=enhancement&projects=&template=feature_request.yml">Request Feature</a>
    ·
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/discussions/1770">FAQ</a>
    ·
    <a href="https://github.com/Tra-Cuu-Sao-Ke/mttq-sao-ke/discussions/new?category=q-a">Ask Question</a>
  </p>
</p>

## Mục tiêu của dự án (Project Purpose)

Bộ dữ liệu này cung cấp thông tin chi tiết được trích xuất từ các bản sao kê công khai của các tài khoản kêu gọi từ thiện được Mặt trận Tổ quốc Việt Nam (MTTQVN) công bố trong đợt bão lũ Yagi vào tháng 9 năm 2024. Dữ liệu bao gồm các giao dịch trong các tài khoản ở các ngân hàng khác nhau của MTTQVN trong suốt thời gian các quỹ từ thiện được kêu gọi, nhằm hỗ trợ giám sát minh bạch các hoạt động quyên góp từ thiện.

This dataset provides detailed information extracted from public statements of charity fundraising accounts published by the Vietnam Fatherland Front (MTTQVN) during Typhoon Yagi in September 2024. The data includes transactions from MTTQVN's accounts at various banks throughout the period of charity fundraising, aimed at transparently monitoring charitable donation activities.

## Nội dung dữ liệu (Dataset Content)

Bộ dữ liệu bao gồm các trường thông tin chính cho mỗi giao dịch:

- Ngày giao dịch (TNXDate)
- Số chứng từ/số tham chiếu (DocNo/RefNo)
- Số tiền chi (Debit)
- Số tiền thu (Credit)
- Số dư cuối mỗi ngày (Balance)
- Mô tả chi tiết giao dịch (Details)
- Các thông tin khác

Các file dữ liệu được lưu dưới dạng CSV, giúp dễ dàng phân tích và truy vấn.

The dataset includes the following key fields for each transaction:

- Transaction Date (TNXDate)
- Document Number/Reference Number (DocNo/RefNo)
- Debit Amount (Debit)
- Credit Amount (Credit)
- End-of-day Balance (Balance)
- Transaction Description (Detail)
- Additional Fields

The data is stored in CSV format for ease of analysis and querying.

## Đóng góp của dự án (Project Contributions)

Bộ dữ liệu này được tạo ra để cung cấp một cơ sở dữ liệu dễ dàng truy cập, minh bạch cho việc kiểm tra các bản sao kê tài khoản từ thiện. Hiện tại, bộ dữ liệu này hỗ trợ các bản sao kê được công bố và cung cấp chi tiết các giao dịch theo từng ngày. Các dự án hoặc hệ thống khác có thể sử dụng bộ dữ liệu này để xây dựng các ứng dụng tra cứu minh bạch hơn.

This dataset was created to provide an accessible, transparent database for reviewing charity account statements. It currently supports published statements and provides detailed daily transaction information. Other projects or systems can utilize this dataset to build more transparent query applications.

## Hướng dẫn sử dụng (How to Use)

Bạn có thể sử dụng các file CSV để phân tích các giao dịch từ thiện hoặc tích hợp vào các hệ thống kiểm tra minh bạch. Dữ liệu có thể được tải về và sử dụng để tạo các hệ thống tra cứu hoặc báo cáo khác nhau về tình trạng thu chi của các quỹ từ thiện.

You can use the CSV files to analyze charity transactions or integrate them into transparency audit systems. The data can be downloaded and used to build query systems or generate various reports on the income and expenses of charity funds.

## Tham gia đóng góp (How to Contribute)

Chúng tôi khuyến khích mọi người đóng góp vào dự án này bằng cách:

- Cập nhật và mở rộng bộ dữ liệu với các bản sao kê từ thiện mới.
- Đóng góp mã nguồn để hỗ trợ tích hợp dữ liệu vào các hệ thống khác.
- Báo cáo lỗi hoặc đề xuất cải tiến bộ dữ liệu.

We encourage contributions to this project by:

- Updating and expanding the dataset with new charity statements.
- Contributing to the codebase to support data integration into other systems.
- Reporting bugs or suggesting improvements to the dataset.

---

## Liên hệ (Contact)

Nếu bạn có bất kỳ câu hỏi hoặc đề xuất nào, vui lòng liên hệ với chúng tôi Linkedin: [Chung Nguyen](https://www.linkedin.com/in/galin-chung-nguyen)

If you have any questions or suggestions, feel free to contact us via Linkedin: [Chung Nguyen](https://www.linkedin.com/in/galin-chung-nguyen)