CREATE TABLE IF NOT EXISTS user_presence (
    user_id        INT          NOT NULL,
    is_online      TINYINT(1)   NOT NULL DEFAULT 0,
    last_seen_at   DATETIME     NULL,
    last_logout_at DATETIME     NULL,
    last_role      VARCHAR(32)  NULL,
    PRIMARY KEY (user_id),
    CONSTRAINT fk_user_presence_user_id
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS audit_log (
    id              BIGINT       NOT NULL AUTO_INCREMENT,
    event_time      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type      VARCHAR(64)  NOT NULL,
    actor_username  VARCHAR(64)  NULL,
    target_username VARCHAR(64)  NULL,
    details         TEXT         NULL,
    success         TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    INDEX idx_audit_event_time (event_time),
    INDEX idx_audit_event_type (event_type),
    INDEX idx_audit_actor (actor_username),
    INDEX idx_audit_target (target_username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

