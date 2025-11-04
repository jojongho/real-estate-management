/**
 * 데이터확인_list에서 모든 컬럼의 UNIQUE 값을 추출하여
 * 개별 참조 시트를 자동 생성하는 Apps Script
 *
 * 사용법:
 * 1. Google Sheets에서 확장 프로그램 → Apps Script
 * 2. 이 코드 붙여넣기
 * 3. createAllReferenceSheets() 함수 실행
 */

function createAllReferenceSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheet = ss.getSheetByName('데이터확인_list');

  if (!sourceSheet) {
    Logger.log('❌ 데이터확인_list 시트를 찾을 수 없습니다!');
    return;
  }

  // 헤더 행 가져오기 (1행)
  const headers = sourceSheet.getRange(1, 1, 1, sourceSheet.getLastColumn()).getValues()[0];

  // 각 컬럼별로 참조 시트 생성
  headers.forEach((header, index) => {
    if (header && header.toString().trim() !== '') {
      createReferenceSheet(ss, sourceSheet, header, index + 1);
    }
  });

  Logger.log('✅ 모든 참조 시트 생성 완료!');
}

/**
 * 개별 참조 시트 생성
 */
function createReferenceSheet(spreadsheet, sourceSheet, columnName, columnIndex) {
  const sheetName = columnName + '_목록';

  // 기존 시트 삭제 (이미 있으면)
  const existingSheet = spreadsheet.getSheetByName(sheetName);
  if (existingSheet) {
    Logger.log(`⚠️ ${sheetName} 시트가 이미 존재합니다. 삭제 후 재생성합니다.`);
    spreadsheet.deleteSheet(existingSheet);
  }

  // 새 시트 생성
  const newSheet = spreadsheet.insertSheet(sheetName);

  // A1에 헤더 입력
  newSheet.getRange('A1').setValue(columnName);

  // A2에 UNIQUE 수식 입력
  const columnLetter = getColumnLetter(columnIndex);
  const formula = `=UNIQUE(FILTER(데이터확인_list!${columnLetter}:${columnLetter}, ` +
                  `데이터확인_list!${columnLetter}:${columnLetter}<>"", ` +
                  `데이터확인_list!${columnLetter}:${columnLetter}<>"${columnName}"))`;

  newSheet.getRange('A2').setFormula(formula);

  // 헤더 서식 설정
  newSheet.getRange('A1').setFontWeight('bold').setBackground('#4285F4').setFontColor('#FFFFFF');

  // 열 너비 자동 조정
  newSheet.autoResizeColumn(1);

  Logger.log(`✅ ${sheetName} 생성 완료`);
}

/**
 * 컬럼 인덱스를 알파벳으로 변환 (1 → A, 2 → B, ...)
 */
function getColumnLetter(columnIndex) {
  let temp, letter = '';
  while (columnIndex > 0) {
    temp = (columnIndex - 1) % 26;
    letter = String.fromCharCode(temp + 65) + letter;
    columnIndex = (columnIndex - temp - 1) / 26;
  }
  return letter;
}

/**
 * 특정 컬럼만 선택적으로 생성
 *
 * 사용 예시:
 * createSelectedReferenceSheets(['거래유형', '난방방식', '주택유형'])
 */
function createSelectedReferenceSheets(columnNames) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheet = ss.getSheetByName('데이터확인_list');

  if (!sourceSheet) {
    Logger.log('❌ 데이터확인_list 시트를 찾을 수 없습니다!');
    return;
  }

  const headers = sourceSheet.getRange(1, 1, 1, sourceSheet.getLastColumn()).getValues()[0];

  columnNames.forEach(columnName => {
    const columnIndex = headers.indexOf(columnName) + 1;
    if (columnIndex > 0) {
      createReferenceSheet(ss, sourceSheet, columnName, columnIndex);
    } else {
      Logger.log(`⚠️ "${columnName}" 컬럼을 찾을 수 없습니다.`);
    }
  });

  Logger.log('✅ 선택한 참조 시트 생성 완료!');
}

/**
 * 통합 고정값 시트 생성 (한 시트에 모든 목록)
 */
function createUnifiedReferenceSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheet = ss.getSheetByName('데이터확인_list');

  if (!sourceSheet) {
    Logger.log('❌ 데이터확인_list 시트를 찾을 수 없습니다!');
    return;
  }

  // 통합 시트 생성
  const unifiedSheetName = '고정값_통합';
  let unifiedSheet = ss.getSheetByName(unifiedSheetName);

  if (unifiedSheet) {
    ss.deleteSheet(unifiedSheet);
  }

  unifiedSheet = ss.insertSheet(unifiedSheetName);

  // 헤더 행 가져오기
  const headers = sourceSheet.getRange(1, 1, 1, sourceSheet.getLastColumn()).getValues()[0];

  // 각 컬럼별로 UNIQUE 수식 생성
  headers.forEach((header, index) => {
    if (header && header.toString().trim() !== '') {
      const colIndex = index + 1;
      const columnLetter = getColumnLetter(colIndex);

      // 헤더 입력 (1행)
      unifiedSheet.getRange(1, colIndex).setValue(header);

      // UNIQUE 수식 입력 (2행)
      const formula = `=UNIQUE(FILTER(데이터확인_list!${columnLetter}:${columnLetter}, ` +
                      `데이터확인_list!${columnLetter}:${columnLetter}<>"", ` +
                      `데이터확인_list!${columnLetter}:${columnLetter}<>"${header}"))`;

      unifiedSheet.getRange(2, colIndex).setFormula(formula);
    }
  });

  // 헤더 서식 설정
  unifiedSheet.getRange(1, 1, 1, headers.length)
    .setFontWeight('bold')
    .setBackground('#4285F4')
    .setFontColor('#FFFFFF');

  // 모든 열 너비 자동 조정
  for (let i = 1; i <= headers.length; i++) {
    unifiedSheet.autoResizeColumn(i);
  }

  Logger.log(`✅ ${unifiedSheetName} 생성 완료!`);
  Logger.log(`📊 총 ${headers.filter(h => h).length}개 컬럼 처리됨`);
}

/**
 * 메뉴에 커스텀 함수 추가
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🔧 참조 시트 생성')
    .addItem('📋 모든 컬럼 → 개별 시트', 'createAllReferenceSheets')
    .addItem('📊 통합 시트 생성', 'createUnifiedReferenceSheet')
    .addSeparator()
    .addItem('✨ 주요 컬럼만 생성', 'createMainReferenceSheets')
    .addToUi();
}

/**
 * 자주 사용하는 주요 컬럼만 생성
 */
function createMainReferenceSheets() {
  const mainColumns = [
    '거래유형',
    '난방방식',
    '주택유형',
    '용도지역',
    '지목',
    '건축물구조',
    '성별'
  ];

  createSelectedReferenceSheets(mainColumns);
}
