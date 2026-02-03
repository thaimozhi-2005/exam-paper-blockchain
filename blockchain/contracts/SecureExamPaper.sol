// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SecureExamPaper
 * @dev Smart contract for secure exam paper storage with encryption and time-lock
 */
contract SecureExamPaper {
    
    // Struct to store exam paper metadata
    struct ExamPaper {
        string collegeId;           // College identifier
        string subjectCode;         // Subject code
        string documentHash;        // SHA-256 hash of encrypted document
        uint256 timestamp;          // Upload timestamp
        address owner;              // Admin who uploaded
        bool verified;              // Verification status
        uint256 examDateTime;       // Scheduled exam date/time (Unix timestamp)
        string encryptedAESKey;     // RSA-encrypted AES key
        string principalEmail;      // Principal's email
    }
    
    // Mapping from paper ID to ExamPaper
    mapping(uint256 => ExamPaper) public papers;
    
    // Auto-incrementing paper ID counter
    uint256 public paperCount = 0;
    
    // Mapping to prevent duplicate hashes
    mapping(string => bool) private hashExists;
    
    // Events for tracking
    event PaperStored(
        uint256 indexed paperId,
        string documentHash,
        string collegeId,
        string subjectCode,
        uint256 examDateTime,
        address indexed owner
    );
    
    event PaperVerified(
        uint256 indexed paperId,
        address indexed verifier,
        uint256 timestamp
    );
    
    /**
     * @dev Store a new exam paper on the blockchain
     * @param _collegeId College identifier
     * @param _subjectCode Subject code
     * @param _documentHash SHA-256 hash of the encrypted document
     * @param _examDateTime Scheduled exam date/time
     * @param _encryptedAESKey RSA-encrypted AES key
     * @param _principalEmail Principal's email address
     * @return paperId The ID of the stored paper
     */
    function storePaper(
        string memory _collegeId,
        string memory _subjectCode,
        string memory _documentHash,
        uint256 _examDateTime,
        string memory _encryptedAESKey,
        string memory _principalEmail
    ) public returns (uint256) {
        // Validate inputs
        require(bytes(_collegeId).length > 0, "College ID cannot be empty");
        require(bytes(_subjectCode).length > 0, "Subject code cannot be empty");
        require(bytes(_documentHash).length > 0, "Document hash cannot be empty");
        require(_examDateTime > block.timestamp, "Exam date must be in the future");
        require(bytes(_encryptedAESKey).length > 0, "Encrypted AES key cannot be empty");
        require(bytes(_principalEmail).length > 0, "Principal email cannot be empty");
        
        // Check for duplicate hash
        require(!hashExists[_documentHash], "Document hash already exists");
        
        // Increment paper count
        paperCount++;
        
        // Create new exam paper
        papers[paperCount] = ExamPaper({
            collegeId: _collegeId,
            subjectCode: _subjectCode,
            documentHash: _documentHash,
            timestamp: block.timestamp,
            owner: msg.sender,
            verified: false,
            examDateTime: _examDateTime,
            encryptedAESKey: _encryptedAESKey,
            principalEmail: _principalEmail
        });
        
        // Mark hash as used
        hashExists[_documentHash] = true;
        
        // Emit event
        emit PaperStored(
            paperCount,
            _documentHash,
            _collegeId,
            _subjectCode,
            _examDateTime,
            msg.sender
        );
        
        return paperCount;
    }
    
    /**
     * @dev Get exam paper details by ID
     * @param _paperId The ID of the paper to retrieve
     * @return collegeId College identifier
     * @return subjectCode Subject code
     * @return documentHash Document hash
     * @return timestamp Upload timestamp
     * @return owner Owner address
     * @return verified Verification status
     * @return examDateTime Exam date/time
     * @return encryptedAESKey Encrypted AES key
     * @return principalEmail Principal email
     */
    function getPaper(uint256 _paperId) public view returns (
        string memory collegeId,
        string memory subjectCode,
        string memory documentHash,
        uint256 timestamp,
        address owner,
        bool verified,
        uint256 examDateTime,
        string memory encryptedAESKey,
        string memory principalEmail
    ) {
        require(_paperId > 0 && _paperId <= paperCount, "Invalid paper ID");
        
        ExamPaper memory paper = papers[_paperId];
        
        return (
            paper.collegeId,
            paper.subjectCode,
            paper.documentHash,
            paper.timestamp,
            paper.owner,
            paper.verified,
            paper.examDateTime,
            paper.encryptedAESKey,
            paper.principalEmail
        );
    }
    
    /**
     * @dev Verify a paper (called after successful decryption and validation)
     * @param _paperId The ID of the paper to verify
     */
    function verifyPaper(uint256 _paperId) public {
        require(_paperId > 0 && _paperId <= paperCount, "Invalid paper ID");
        require(!papers[_paperId].verified, "Paper already verified");
        
        papers[_paperId].verified = true;
        
        emit PaperVerified(_paperId, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Check if exam time has arrived (time-lock mechanism)
     * @param _paperId The ID of the paper to check
     * @return bool True if exam time has arrived
     */
    function isExamTimeReached(uint256 _paperId) public view returns (bool) {
        require(_paperId > 0 && _paperId <= paperCount, "Invalid paper ID");
        return block.timestamp >= papers[_paperId].examDateTime;
    }
    
    /**
     * @dev Get the total number of papers stored
     * @return uint256 Total paper count
     */
    function getTotalPapers() public view returns (uint256) {
        return paperCount;
    }
    
    /**
     * @dev Check if a document hash already exists
     * @param _documentHash The hash to check
     * @return bool True if hash exists
     */
    function doesHashExist(string memory _documentHash) public view returns (bool) {
        return hashExists[_documentHash];
    }
}
