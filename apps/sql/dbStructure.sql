-------- Table Code Start -------------------------
ALTER TABLE ROBI_RPA1.RPA_DIV_ERASE_VOUCHER
 DROP PRIMARY KEY CASCADE;

DROP TABLE ROBI_RPA1.RPA_DIV_ERASE_VOUCHER CASCADE CONSTRAINTS;

CREATE TABLE ROBI_RPA1.RPA_DIV_ERASE_VOUCHER
(
  ID                   INTEGER,
  COMPLAIN_ID          VARCHAR2(255 CHAR),
  MSISDN               NUMBER,
  VISIBLE_CARD_NUMBER  VARCHAR2(255 CHAR),
  CARD_SL              VARCHAR2(255 CHAR),
  COMPLAIN_STATUS      INTEGER,
  REMARKS              VARCHAR2(255 CHAR),
  CREATED_AT           DATE
)
TABLESPACE USERS
PCTUSED    0
PCTFREE    10
INITRANS   1
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            NEXT             1M
            MINEXTENTS       1
            MAXEXTENTS       UNLIMITED
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
           )
LOGGING
NOCOMPRESS
NOCACHE
NOPARALLEL
MONITORING;

------------- Sequence Code Start-------------------
DROP SEQUENCE ROBI_RPA1.RPA_DIV_ERASE_VOUCHER_SEQ;

CREATE SEQUENCE ROBI_RPA1.RPA_DIV_ERASE_VOUCHER_SEQ
  START WITH 41
  MAXVALUE 99999999999999999
  MINVALUE 1
  NOCYCLE
  CACHE 20
  NOORDER;

-------- Trigger Code Start -------------------------
CREATE OR REPLACE TRIGGER ROBI_RPA1.RPA_DIV_ERASE_VOUCHER_TR
BEFORE INSERT ON ROBI_RPA1.RPA_DIV_ERASE_VOUCHER
FOR EACH ROW
BEGIN
  SELECT RPA_DIV_ERASE_VOUCHER_SEQ.NEXTVAL
  INTO   :new.id
  FROM   dual;
END;
/


ALTER TABLE ROBI_RPA1.RPA_DIV_ERASE_VOUCHER ADD (
  PRIMARY KEY
 (ID)
    USING INDEX
    TABLESPACE USERS
    PCTFREE    10
    INITRANS   2
    MAXTRANS   255
    STORAGE    (
                INITIAL          64K
                NEXT             1M
                MINEXTENTS       1
                MAXEXTENTS       UNLIMITED
                PCTINCREASE      0
               ));
