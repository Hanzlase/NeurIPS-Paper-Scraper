package a;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.time.Instant;
import java.time.Duration;
import javax.swing.*;
import javax.swing.border.*;
import javax.swing.table.*;
import java.awt.*;
import java.io.FileWriter;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutionException;

public class NeurIPSscraper extends JFrame {
    private static final String[] USER_AGENTS = {
    		    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
		        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
		        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
		        "Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
		        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
		        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
		        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
		        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
		        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
		        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
		        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
		        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
		        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
		        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
		        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
		        "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
		    };

    private JTextField startYearField;
    private JTextField endYearField;
    private JTextField downloadDirField;
    private JButton scrapeButton;
    private JButton downloadButton;
    private JTable paperTable;
    private DefaultTableModel tableModel;
    private JProgressBar progressBar;
    private JTextArea logArea;
    private JLabel timerLabel;
    private List<String[]> metadataList;

    private static final Color PRIMARY_COLOR = new Color(41, 128, 185);    
    private static final Color SECONDARY_COLOR = new Color(52, 152, 219);
    private static final Color BACKGROUND_COLOR = new Color(236, 240, 241);
    private static final Color ACCENT_COLOR = new Color(46, 204, 113);     
    private static final Color TEXT_COLOR = new Color(44, 62, 80);        

    public NeurIPSscraper() {
        initializeGUI();
    }

    private void initializeGUI() {
        setTitle("NeurIPS Paper Scraper");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));
        setExtendedState(JFrame.MAXIMIZED_BOTH);
        getContentPane().setBackground(BACKGROUND_COLOR);
        
        timerLabel = new JLabel("Time: 0s");
        timerLabel.setFont(new Font("Arial", Font.BOLD, 14));
        timerLabel.setForeground(Color.WHITE);
        timerLabel.setBorder(BorderFactory.createEmptyBorder(0, 20, 10, 20));
        timerLabel.setHorizontalAlignment(SwingConstants.RIGHT);

        JPanel mainPanel = new JPanel(new BorderLayout(15, 15));
        mainPanel.setBackground(BACKGROUND_COLOR);
        mainPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        // Creating and adding the header panel
        mainPanel.add(createHeaderPanel(), BorderLayout.NORTH);
        
        // Content panel
        mainPanel.add(createContentPanel(), BorderLayout.CENTER);
        
        //Footer Panel
        mainPanel.add(createFooterPanel(), BorderLayout.SOUTH);

        add(mainPanel);

    }

    private JPanel createHeaderPanel() {
        JPanel headerPanel = new JPanel(new BorderLayout(10, 10));
        headerPanel.setBackground(BACKGROUND_COLOR);

        // Title Panel
        JPanel titlePanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        titlePanel.setBackground(PRIMARY_COLOR);
        JLabel titleLabel = new JLabel("NeurIPS Paper Scraper");
        titleLabel.setFont(new Font("Arial", Font.BOLD, 24));
        titleLabel.setForeground(Color.WHITE);
        titleLabel.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        titlePanel.add(titleLabel);

        // Input Panel
        JPanel inputPanel = new JPanel(new GridBagLayout());
        inputPanel.setBackground(BACKGROUND_COLOR);
        inputPanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEmptyBorder(10, 10, 10, 10),
            BorderFactory.createLineBorder(SECONDARY_COLOR, 1, true)
        ));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(5, 5, 5, 5);

        // Style input fields
        startYearField = createStyledTextField("2019");
        endYearField = createStyledTextField("2023");
        downloadDirField = createStyledTextField("pdfs");

        // Add components with GridBagLayout
        addLabelAndField(inputPanel, "Start Year:", startYearField, gbc, 0);
        addLabelAndField(inputPanel, "End Year:", endYearField, gbc, 1);
        addLabelAndField(inputPanel, "Download Directory:", downloadDirField, gbc, 2);

        // Buttons Panel
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 10));
        buttonPanel.setBackground(BACKGROUND_COLOR);

        scrapeButton = createStyledButton("Scrape Metadata", PRIMARY_COLOR);
        scrapeButton.addActionListener(e -> scrapeMetadata());

        downloadButton = createStyledButton("Download PDFs", ACCENT_COLOR);
        downloadButton.setEnabled(false);
        downloadButton.addActionListener(e -> downloadPDFs());

        buttonPanel.add(scrapeButton);
        buttonPanel.add(downloadButton);

        // Combine panels
        headerPanel.add(titlePanel, BorderLayout.NORTH);
        headerPanel.add(inputPanel, BorderLayout.CENTER);
        headerPanel.add(buttonPanel, BorderLayout.SOUTH);

        return headerPanel;
    }

    private JPanel createContentPanel() {
        JPanel contentPanel = new JPanel(new BorderLayout(10, 10));
        contentPanel.setBackground(BACKGROUND_COLOR);

        // Table Panel
        tableModel = new DefaultTableModel(new String[]{"Title", "Authors", "Year", "PDF Link"}, 0);
        paperTable = new JTable(tableModel) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        
        // Style the table
        paperTable.setFillsViewportHeight(true);
        paperTable.setShowGrid(true);
        paperTable.setGridColor(SECONDARY_COLOR);
        paperTable.setBackground(Color.WHITE);
        paperTable.setForeground(TEXT_COLOR);
        paperTable.setSelectionBackground(SECONDARY_COLOR);
        paperTable.setSelectionForeground(Color.WHITE);
        paperTable.setFont(new Font("Arial", Font.PLAIN, 14));
        paperTable.getTableHeader().setFont(new Font("Arial", Font.BOLD, 14));
        paperTable.getTableHeader().setBackground(PRIMARY_COLOR);
        paperTable.setRowHeight(25);

        // Set column widths
        TableColumnModel columnModel = paperTable.getColumnModel();
        columnModel.getColumn(0).setPreferredWidth(300); // Title
        columnModel.getColumn(1).setPreferredWidth(200); // Authors
        columnModel.getColumn(2).setPreferredWidth(70);  // Year
        columnModel.getColumn(3).setPreferredWidth(200); // PDF Link

        JScrollPane tableScrollPane = new JScrollPane(paperTable);
        tableScrollPane.setBorder(BorderFactory.createLineBorder(SECONDARY_COLOR));

        contentPanel.add(tableScrollPane, BorderLayout.CENTER);

        return contentPanel;
    }

    private JPanel createFooterPanel() {
        JPanel footerPanel = new JPanel(new BorderLayout(10, 10));
        footerPanel.setBackground(BACKGROUND_COLOR);

        // Progress Panel
        progressBar = new JProgressBar(0, 100);
        progressBar.setStringPainted(true);
        progressBar.setForeground(ACCENT_COLOR);
        progressBar.setBackground(Color.WHITE);
        progressBar.setBorder(BorderFactory.createLineBorder(SECONDARY_COLOR));
        progressBar.setPreferredSize(new Dimension(progressBar.getPreferredSize().width, 25));

        // Log Panel
        logArea = new JTextArea(6, 80);
        logArea.setEditable(false);
        logArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        logArea.setBackground(Color.WHITE);
        logArea.setForeground(TEXT_COLOR);
        logArea.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

        JScrollPane logScrollPane = new JScrollPane(logArea);
        logScrollPane.setBorder(BorderFactory.createLineBorder(SECONDARY_COLOR));

        footerPanel.add(progressBar, BorderLayout.NORTH);
        footerPanel.add(logScrollPane, BorderLayout.CENTER);

        return footerPanel;
    }

    private JTextField createStyledTextField(String text) {
        JTextField textField = new JTextField(text);
        textField.setFont(new Font("Arial", Font.PLAIN, 14));
        textField.setForeground(TEXT_COLOR);
        textField.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(SECONDARY_COLOR),
            BorderFactory.createEmptyBorder(5, 7, 5, 7)
        ));
        return textField;
    }

    private JButton createStyledButton(String text, Color backgroundColor) {
        JButton button = new JButton(text);
        button.setFont(new Font("Arial", Font.BOLD, 14));
        button.setForeground(Color.WHITE);
        button.setBackground(backgroundColor);
        button.setFocusPainted(false);
        button.setBorderPainted(false);
        button.setPreferredSize(new Dimension(150, 35));
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));

        button.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                button.setBackground(backgroundColor.brighter());
            }

            public void mouseExited(java.awt.event.MouseEvent evt) {
                button.setBackground(backgroundColor);
            }
        });

        return button;
    }

    private void addLabelAndField(JPanel panel, String labelText, JComponent field, GridBagConstraints gbc, int row) {
        JLabel label = new JLabel(labelText);
        label.setFont(new Font("Arial", Font.BOLD, 14));
        label.setForeground(TEXT_COLOR);

        gbc.gridx = 0;
        gbc.gridy = row;
        gbc.weightx = 0.3;
        panel.add(label, gbc);

        gbc.gridx = 1;
        gbc.weightx = 0.7;
        panel.add(field, gbc);
    }
    
    private static String getRandomUserAgent() {
        Random random = new Random();
        return USER_AGENTS[random.nextInt(USER_AGENTS.length)];
    }

    private void log(String message) {
        SwingUtilities.invokeLater(() -> {
            logArea.append(message + "\n");
            logArea.setCaretPosition(logArea.getDocument().getLength());
        });
    }

    private List<String[]> collectMetadata(int startYear, int endYear, String csvPath) throws IOException {
        List<String[]> metadataList = new ArrayList<>();
        String baseUrl = "https://papers.nips.cc/paper/";
        
        try (FileWriter metadataWriter = new FileWriter(csvPath)) {
            metadataWriter.append("Title,Authors,Year,PDF Link\n");

            for (int year = startYear; year <= endYear; year++) {
                String yearUrl = baseUrl + year;
                log("Processing year: " + year);
                log("URL: " + yearUrl);
                
                try {
                    Document doc = Jsoup.connect(yearUrl)
                            .userAgent(getRandomUserAgent())
                            .timeout(30000)
                            .get();

                    Elements paperLinks = doc.select("a[title='paper title']");
                    log("Found " + paperLinks.size() + " papers for year " + year);

                    for (Element paperLink : paperLinks) {
                        try {
                            String title = paperLink.text().trim();
                            
                            String authors = "";
                            Element authorElement = paperLink.nextElementSibling();
                            if (authorElement != null && authorElement.tagName().equals("i")) {
                                authors = authorElement.text().trim();
                            }

                            String abstractUrl = paperLink.attr("href");
                            String pdfLink = "";
                            if (abstractUrl.contains("Abstract")) {
                                String hash = abstractUrl.substring(abstractUrl.lastIndexOf('/') + 1)
                                                       .replace("-Abstract.html", "");
                                pdfLink = String.format("https://papers.nips.cc/paper_files/paper/%d/file/%s-Paper.pdf", 
                                                      year, hash);
                            }

                            if (!title.isEmpty() && !pdfLink.isEmpty()) {
                                String csvLine = String.format("\"%s\",\"%s\",\"%d\",\"%s\"\n",
                                        title.replace("\"", "\"\""),
                                        authors.replace("\"", "\"\""),
                                        year,
                                        pdfLink);
                                
                                metadataWriter.append(csvLine);
                                metadataWriter.flush();

                                metadataList.add(new String[]{title, authors, String.valueOf(year), pdfLink});
                            }

                        } catch (Exception e) {
                            log("Error processing paper: " + e.getMessage());
                        }
                    }

                } catch (IOException e) {
                    log("Error processing year " + year + ": " + e.getMessage());
                }
            }
        }
        
        log("Metadata collection completed. Total papers: " + metadataList.size());
        return metadataList;
    }

    private void scrapeMetadata() {
        int startYear = Integer.parseInt(startYearField.getText());
        int endYear = Integer.parseInt(endYearField.getText());
        String csvPath = Paths.get("").toAbsolutePath().toString() + "/metadata.csv";

        scrapeButton.setEnabled(false);
        
        Thread timerThread = new Thread(() -> {
            Instant startTime = Instant.now();
            while (!Thread.interrupted()) {
                Duration duration = Duration.between(startTime, Instant.now());
                long seconds = duration.getSeconds();
                SwingUtilities.invokeLater(() -> 
                    timerLabel.setText(String.format("Time: %02d:%02d:%02d", 
                        seconds / 3600, (seconds % 3600) / 60, seconds % 60)));
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    break;
                }
            }
        });

        SwingWorker<List<String[]>, Void> worker = new SwingWorker<>() {
            private Thread timerThreadRef = timerThread;

            @Override
            protected List<String[]> doInBackground() throws Exception {
                try {
                    Files.createDirectories(Paths.get(downloadDirField.getText()));
                    return collectMetadata(startYear, endYear, csvPath);
                } catch (IOException e) {
                    log("Error creating download directory: " + e.getMessage());
                    return new ArrayList<>();
                }
            }

            @Override
            protected void done() {
                try {
                    metadataList = get();
                    updateTableModel(metadataList);
                    downloadButton.setEnabled(!metadataList.isEmpty());
                    
                    timerThreadRef.interrupt();
                    String finalTime = timerLabel.getText();
                    
                    JOptionPane.showMessageDialog(NeurIPSscraper.this,
                        String.format("Scraped %d papers\nTotal time: %s",
                            metadataList.size(), finalTime.substring(6)),
                        "Scraping Complete",
                        JOptionPane.INFORMATION_MESSAGE);
                    
                    scrapeButton.setEnabled(true);
                    
                } catch (InterruptedException | ExecutionException e) {
                    log("Error during scraping: " + e.getMessage());
                    timerThreadRef.interrupt();
                    scrapeButton.setEnabled(true);
                }
            }
        };

        timerThread.start();
        worker.execute();
    }

    private void updateTableModel(List<String[]> metadata) {
        tableModel.setRowCount(0);
        for (String[] paper : metadata) {
            tableModel.addRow(paper);
        }
    }

    private boolean downloadPDFWithRetry(String pdfUrl, String destinationPath, int maxRetries) {
        int attempt = 0;
        while (attempt < maxRetries) {
            try {
                downloadPDF(pdfUrl, destinationPath);
                return true;
            } catch (IOException e) {
                attempt++;
                log("Attempt " + attempt + " failed: " + e.getMessage());
                if (attempt >= maxRetries) {
                    return false;
                }
            }
        }
        return false;
    }

    private void downloadPDF(String pdfUrl, String destinationPath) throws IOException {
        URL url = new URL(pdfUrl);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        connection.setConnectTimeout(20000);
        connection.setReadTimeout(20000);
        connection.setRequestProperty("User-Agent", getRandomUserAgent());
        connection.setInstanceFollowRedirects(true);

        try (var inputStream = connection.getInputStream();
             var outputStream = new java.io.FileOutputStream(destinationPath)) {

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }
        } catch (IOException e) {
            log("Error downloading PDF: " + e.getMessage());
            throw e;
        } finally {
            connection.disconnect();
        }
    }

    private void downloadPDFs() {
        String downloadDir = downloadDirField.getText();

        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() throws Exception {
                int totalPapers = metadataList.size();
                
                for (int i = 0; i < totalPapers; i++) {
                    String[] paper = metadataList.get(i);
                    try {
                        String pdfUrl = paper[3];
                        String title = paper[0].replaceAll("[^a-zA-Z0-9]", "_");
                        String destinationPath = downloadDir + "/" + title + "_" + paper[2] + ".pdf";
                        
                        boolean downloaded = downloadPDFWithRetry(pdfUrl, destinationPath, 3);
                        log(downloaded ? "Downloaded: " + title : "Failed to download: " + title);
                        
                        int progress = (int) (((i + 1) / (double) totalPapers) * 100);
                        setProgress(progress);
                    } catch (Exception e) {
                        log("Error downloading PDF: " + e.getMessage());
                    }
                }
                return null;
            }

            @Override
            protected void done() {
                try {
                    get();
                    JOptionPane.showMessageDialog(NeurIPSscraper.this, 
                        "PDF Download Complete", 
                        "Download Finished", 
                        JOptionPane.INFORMATION_MESSAGE);
                } catch (InterruptedException | ExecutionException e) {
                    log("Download error: " + e.getMessage());
                }
            }
        };

        worker.addPropertyChangeListener(evt -> {
            if ("progress".equals(evt.getPropertyName())) {
                progressBar.setValue((Integer) evt.getNewValue());
            }
        });

        worker.execute();
    }
    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        SwingUtilities.invokeLater(() -> {
            new NeurIPSscraper().setVisible(true);
        });
    }
}