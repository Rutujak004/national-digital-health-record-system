// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PatientRecords {

    struct Record {
        uint256 patientId;
        string hashValue;
        uint256 timestamp;
    }

    // Mapping of patientId -> list of blockchain records
    mapping(uint256 => Record[]) public records;

    // Add a new record for a patient
    function addRecord(uint256 patientId, string memory hashValue) public {
        records[patientId].push(
            Record({
                patientId: patientId,
                hashValue: hashValue,
                timestamp: block.timestamp
            })
        );
    }

    // Get all records for a specific patient
    function getRecords(uint256 patientId) public view returns (Record[] memory) {
        return records[patientId];
    }
}
