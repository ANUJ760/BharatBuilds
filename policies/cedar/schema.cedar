// Base Cedar schema for MicroAgent

entity User {
    organization_id: String,
    role: String,
};

entity Organization {};

entity Tool {
    name: String,
    risk_level: String,
};

entity Workflow {
    organization_id: String,
};

entity DriveResource {
    organization_id: String,
};

action ExecuteTool;
action ReadDocument;
action ListDocuments;
action UpdateDocument;
