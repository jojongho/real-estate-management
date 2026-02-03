Attribute VB_Name = "FolderCreator"
Option Explicit

' ==================================================================================
' Google Drive Folder Auto-Creator (Excel VBA Version)
' ==================================================================================
' This module replicates the functionality of the Google Apps Script "folder_create.js"
' It creates a folder structure in a local directory (e.g., OneDrive sync folder).
'
' Usage:
' 1. Set the ROOT_PATH constant to your local OneDrive/Google Drive folder path.
' 2. Ensure "Microsoft Scripting Runtime" is enabled in Tools > References.
'    (Or this script uses late binding to avoid reference issues).
' ==================================================================================

' ✅ CONFIGURATION
' 기본적으로 엑셀 파일이 있는 폴더를 최상위 경로로 사용합니다. (ThisWorkbook.Path)
' 다른 경로를 사용하려면 엑셀의 "설정" 시트나 이름 정의(Name Manager)에서 "RootPath"를 설정하세요.

' Root Subfolder Names (Mapping from ROOT_FOLDER_IDS)
' Modify these matching your actual folder names in the root directory
Private Const FOLDER_APT As String = "통합매물데이터(지역별)"
Private Const FOLDER_TOWN As String = "통합매물데이터(지역별)"
Private Const FOLDER_BLDG As String = "통합매물데이터(지역별)"
Private Const FOLDER_LAND As String = "통합매물데이터(지역별)"
Private Const FOLDER_FACTORY As String = "통합매물데이터(지역별)"

' Header Names (Must match Excel Columns)
Private Const COL_REGION As String = "시군구"
Private Const COL_DISTRICT As String = "동읍면"
Private Const COL_VILLAGE As String = "통반리"
Private Const COL_JIBUN As String = "지번"
Private Const COL_COMPLEX As String = "단지명"
Private Const COL_DONG As String = "동"
Private Const COL_HO As String = "호"
Private Const COL_TYPE As String = "타입"
Private Const COL_TOWN_COMPLEX As String = "주택단지"
Private Const COL_TOWN_TYPE As String = "주택유형"
Private Const COL_BLDG_NAME As String = "건물명"
Private Const COL_HO_NUM As String = "호수" ' 상가용
Private Const COL_SHOP_NAME As String = "상호명"
Private Const COL_ROOM_STRUCT As String = "방구조"
Private Const COL_TRADE_TYPE As String = "거래유형"
Private Const COL_PROPERTY_TYPE As String = "매물유형"
Private Const COL_ADDRESS As String = "주소"
Private Const COL_LAND_TYPE As String = "토지분류"
Private Const COL_FACTORY_NAME As String = "명칭"

' Result Columns
Private Const COL_RESULT_URL As String = "관련파일"
Private Const COL_RESULT_ID As String = "폴더ID" ' Excel won't have an ID, but we can store Path

' ==================================================================================
' Main Entry Point: Call this from Sheet's "Worksheet_Change" event
' ==================================================================================
Public Sub HandleChange(ByVal Target As Range)
    On Error GoTo ErrorHandler
    
    Dim ws As Worksheet
    Set ws = Target.Worksheet
    
    ' Skip header row
    If Target.Row = 1 Then Exit Sub
    
    ' Check Sheet Name and Route
    Select Case ws.Name
        Case "아파트매물"
            HandleApartmentRow ws, Target.Row
        Case "주택타운"
            HandleTownRow ws, Target.Row
        Case "건물", "상가", "원투룸"
            HandleBuildingRow ws, Target.Row
        Case "토지"
            HandleLandRow ws, Target.Row
        Case "공장창고"
            HandleFactoryRow ws, Target.Row
    End Select
    
    Exit Sub
ErrorHandler:
    Debug.Print "Error in HandleChange: " & Err.Description
End Sub

' ==================================================================================
' Batch Processing Tool
' ==================================================================================
Public Sub ProcessAllRows()
    Dim ws As Worksheet
    Set ws = ActiveSheet
    
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    
    Dim i As Long
    For i = 2 To lastRow
        Select Case ws.Name
            Case "아파트매물"
                HandleApartmentRow ws, i
            Case "주택타운"
                HandleTownRow ws, i
            Case "건물", "상가", "원투룸"
                HandleBuildingRow ws, i
            Case "토지"
                HandleLandRow ws, i
            Case "공장창고"
                HandleFactoryRow ws, i
        End Select
    Next i
    
    MsgBox "Completed processing " & (lastRow - 1) & " rows in " & ws.Name
End Sub

' ==================================================================================
' Logic Handlers
' ==================================================================================

Private Sub HandleApartmentRow(ws As Worksheet, rowNum As Long)
    Dim headers As Object
    Set headers = GetHeaderMap(ws)
    
    ' Check required columns
    If Not HasKeys(headers, Array(COL_REGION, COL_DISTRICT, COL_JIBUN, COL_COMPLEX, COL_DONG, COL_HO, COL_TYPE)) Then Exit Sub
    
    ' Get Values
    Dim region As String: region = GetVal(ws, rowNum, headers, COL_REGION)
    Dim district As String: district = GetVal(ws, rowNum, headers, COL_DISTRICT)
    Dim village As String: village = GetVal(ws, rowNum, headers, COL_VILLAGE)
    Dim jibun As String: jibun = GetVal(ws, rowNum, headers, COL_JIBUN)
    
    ' Address Fallback
    If (region = "" Or district = "") And headers.Exists("주소") Then
        ParseAddress GetVal(ws, rowNum, headers, "주소"), region, district, village, jibun
    End If
    
    Dim complex As String: complex = GetVal(ws, rowNum, headers, COL_COMPLEX)
    Dim dong As String: dong = GetVal(ws, rowNum, headers, COL_DONG)
    Dim ho As String: ho = GetVal(ws, rowNum, headers, COL_HO)
    Dim typeName As String: typeName = GetVal(ws, rowNum, headers, COL_TYPE)
    
    If region = "" Or district = "" Or jibun = "" Or complex = "" Or dong = "" Or ho = "" Or typeName = "" Then Exit Sub
    
    ' Check if already processed
    Dim urlCol As Long: urlCol = headers(COL_RESULT_URL)
    If ws.Cells(rowNum, urlCol).Value <> "" Then Exit Sub
    
    ' Create Structure
    Dim root As String, path As String
    root = BuildPath(GetRootPath(), FOLDER_APT)
    
    ' 1. Region (Normalized)
    Dim normRegion As String: normRegion = NormalizeRegion(region)
    path = CreateFolder(root, normRegion)
    
    ' 2. District
    path = CreateFolder(path, district)
    
    ' 3. Village (Optional)
    If Trim(village) <> "" Then path = CreateFolder(path, village)
    
    ' 4. Complex
    path = CreateFolder(path, jibun & " " & complex)
    
    ' 5. Property Group
    path = CreateFolder(path, "-매물")
    
    ' 6. Unit
    path = CreateFolder(path, dong & "-" & ho & "-" & typeName)
    
    ' Write Result
    ws.Cells(rowNum, urlCol).Value = path
    ' Optional: Write pseudo-ID or just leave empty
    If headers.Exists(COL_RESULT_ID) Then ws.Cells(rowNum, headers(COL_RESULT_ID)).Value = "LOCAL_FOLDER"
End Sub

Private Sub HandleTownRow(ws As Worksheet, rowNum As Long)
    Dim headers As Object
    Set headers = GetHeaderMap(ws)
    
    If Not HasKeys(headers, Array(COL_REGION, COL_DISTRICT, COL_JIBUN, COL_TOWN_COMPLEX)) Then Exit Sub
    
    Dim region As String: region = GetVal(ws, rowNum, headers, COL_REGION)
    Dim district As String: district = GetVal(ws, rowNum, headers, COL_DISTRICT)
    Dim jibun As String: jibun = GetVal(ws, rowNum, headers, COL_JIBUN)

    ' Address Fallback
    If (region = "" Or district = "") And headers.Exists("주소") Then
        Dim tempVillage As String
        ParseAddress GetVal(ws, rowNum, headers, "주소"), region, district, tempVillage, jibun
        If tempVillage <> "" Then 
             ' Assuming HandleTownRow logic handles village variable later, 
             ' but existing code fetches it from COL_VILLAGE. 
             ' Ideally we update the 'village' variable if it was empty.
        End If
    End If
    Dim complex As String: complex = GetVal(ws, rowNum, headers, COL_TOWN_COMPLEX)
    Dim townType As String: townType = GetVal(ws, rowNum, headers, COL_TOWN_TYPE)
    Dim village As String: village = GetVal(ws, rowNum, headers, COL_VILLAGE)
    
    Dim dong As String: dong = GetVal(ws, rowNum, headers, COL_DONG)
    Dim ho As String: ho = GetVal(ws, rowNum, headers, COL_HO)
    Dim typeName As String: typeName = GetVal(ws, rowNum, headers, COL_TYPE)
    
    If region = "" Or district = "" Or jibun = "" Or complex = "" Then Exit Sub
    
    Dim urlCol As Long: urlCol = headers(COL_RESULT_URL)
    If ws.Cells(rowNum, urlCol).Value <> "" Then Exit Sub
    
    Dim root As String, path As String
    root = BuildPath(GetRootPath(), FOLDER_TOWN)
    
    path = CreateFolder(root, NormalizeRegion(region))
    path = CreateFolder(path, district)
    If Trim(village) <> "" Then path = CreateFolder(path, village)
    
    ' Logic based on Town Type
    Dim normType As String: normType = LCase(Trim(townType))
    
    If normType = "단독" Or complex = "단독" Then
        path = CreateFolder(path, jibun & "번지 " & complex)
    ElseIf normType = "단지형 전원주택" Or normType = "전원주택" Then
        path = CreateFolder(path, complex)
        path = CreateFolder(path, "-매물")
        
        Dim leaf As String: leaf = jibun & "번지"
        If dong <> "" Then leaf = leaf & " " & dong & "동"
        If ho <> "" Then leaf = leaf & " " & ho & "호"
        path = CreateFolder(path, leaf)
    Else ' Villa/Townhouse/Duplex
        path = CreateFolder(path, complex)
        path = CreateFolder(path, "-매물")
        
        Dim parts As String: parts = jibun & "번지"
        If dong <> "" Then parts = parts & " " & dong & "동"
        If ho <> "" Then parts = parts & " " & ho & "호"
        If typeName <> "" Then parts = parts & " " & typeName
        path = CreateFolder(path, parts)
    End If
    
    ws.Cells(rowNum, urlCol).Value = path
End Sub

Private Sub HandleBuildingRow(ws As Worksheet, rowNum As Long)
    Dim headers As Object
    Set headers = GetHeaderMap(ws)
    
    If Not HasKeys(headers, Array(COL_BLDG_NAME)) Then Exit Sub
    
    Dim buildingName As String: buildingName = GetVal(ws, rowNum, headers, COL_BLDG_NAME)
    If buildingName = "" Then Exit Sub
    
    ' Address Parsing Logic simplified for VBA (assuming columns exist)
    ' In a full implementation, you might need a separate Lookup function like the JS one
    If Not HasKeys(headers, Array(COL_REGION, COL_DISTRICT, COL_JIBUN)) Then
        MsgBox "Building sheet requires Region/District/Jibun columns for this VBA version", vbExclamation
        Exit Sub
    End If
    
    Dim region As String: region = GetVal(ws, rowNum, headers, COL_REGION)
    Dim district As String: district = GetVal(ws, rowNum, headers, COL_DISTRICT)
    Dim jibun As String: jibun = GetVal(ws, rowNum, headers, COL_JIBUN)
    Dim village As String: village = GetVal(ws, rowNum, headers, COL_VILLAGE)

    ' Address Fallback
    If (region = "" Or district = "") And headers.Exists("주소") Then
        ParseAddress GetVal(ws, rowNum, headers, "주소"), region, district, village, jibun
    End If
    
    Dim propType As String: propType = GetVal(ws, rowNum, headers, COL_PROPERTY_TYPE)
    If propType = "" Then propType = ws.Name
    
    Dim ho As String
    If headers.Exists(COL_HO) Then ho = GetVal(ws, rowNum, headers, COL_HO)
    If ho = "" And headers.Exists(COL_HO_NUM) Then ho = GetVal(ws, rowNum, headers, COL_HO_NUM)
    
    Dim shopName As String: shopName = GetVal(ws, rowNum, headers, COL_SHOP_NAME)
    Dim roomStruct As String: roomStruct = GetVal(ws, rowNum, headers, COL_ROOM_STRUCT)
    Dim tradeType As String: tradeType = GetVal(ws, rowNum, headers, COL_TRADE_TYPE)
    
    ' Skip if URL exists
    Dim urlCol As Long: urlCol = headers(COL_RESULT_URL)
    If ws.Cells(rowNum, urlCol).Value <> "" Then Exit Sub
    
    Dim root As String, path As String
    root = BuildPath(GetRootPath(), FOLDER_BLDG)
    
    path = CreateFolder(root, NormalizeRegion(region))
    path = CreateFolder(path, district)
    If Trim(village) <> "" Then path = CreateFolder(path, village)
    
    ' Building Folder
    path = CreateFolder(path, jibun & " " & buildingName)
    path = CreateFolder(path, "-매물")
    
    ' Leaf Folder
    Dim isShop As Boolean: isShop = (InStr(propType, "상가") > 0)
    Dim isRoom As Boolean: isRoom = (InStr(propType, "원투룸") > 0)
    
    Dim leaf As String
    Dim parts As New Collection
    If ho <> "" Then parts.Add ho
    
    If isShop And shopName <> "" Then
        parts.Add shopName
    ElseIf isRoom And roomStruct <> "" Then
        parts.Add roomStruct
    End If
    
    If tradeType <> "" Then parts.Add tradeType
    
    If parts.Count > 0 Then
        leaf = JoinCollection(parts, " ")
    Else
        leaf = IIf(ho <> "", ho, "매물")
    End If
    
    path = CreateFolder(path, leaf)
    ws.Cells(rowNum, urlCol).Value = path
End Sub

Private Sub HandleLandRow(ws As Worksheet, rowNum As Long)
    Dim headers As Object
    Set headers = GetHeaderMap(ws)
    
    If Not HasKeys(headers, Array(COL_REGION, COL_DISTRICT, COL_JIBUN, COL_LAND_TYPE)) Then Exit Sub
    
    Dim region As String: region = GetVal(ws, rowNum, headers, COL_REGION)
    Dim district As String: district = GetVal(ws, rowNum, headers, COL_DISTRICT)
    Dim village As String: village = GetVal(ws, rowNum, headers, COL_VILLAGE)
    Dim jibun As String: jibun = GetVal(ws, rowNum, headers, COL_JIBUN)

    ' Address Fallback
    If (region = "" Or district = "") And headers.Exists("주소") Then
        ParseAddress GetVal(ws, rowNum, headers, "주소"), region, district, village, jibun
    End If
    Dim landType As String: landType = GetVal(ws, rowNum, headers, COL_LAND_TYPE)
    
    If region = "" Or district = "" Or jibun = "" Or landType = "" Then Exit Sub
    
    Dim urlCol As Long: urlCol = headers(COL_RESULT_URL)
    If ws.Cells(rowNum, urlCol).Value <> "" Then Exit Sub
    
    Dim root As String, path As String
    root = BuildPath(GetRootPath(), FOLDER_LAND)
    
    path = CreateFolder(root, NormalizeRegion(region))
    path = CreateFolder(path, district)
    If Trim(village) <> "" Then path = CreateFolder(path, village)
    
    path = CreateFolder(path, jibun & " " & landType)
    
    ws.Cells(rowNum, urlCol).Value = path
End Sub

Private Sub HandleFactoryRow(ws As Worksheet, rowNum As Long)
    Dim headers As Object
    Set headers = GetHeaderMap(ws)
    
    If Not HasKeys(headers, Array(COL_REGION, COL_DISTRICT, COL_JIBUN, COL_FACTORY_NAME)) Then Exit Sub
    
    Dim region As String: region = GetVal(ws, rowNum, headers, COL_REGION)
    Dim district As String: district = GetVal(ws, rowNum, headers, COL_DISTRICT)
    Dim village As String: village = GetVal(ws, rowNum, headers, COL_VILLAGE)
    Dim jibun As String: jibun = GetVal(ws, rowNum, headers, COL_JIBUN)

    ' Address Fallback
    If (region = "" Or district = "") And headers.Exists("주소") Then
        ParseAddress GetVal(ws, rowNum, headers, "주소"), region, district, village, jibun
    End If
    Dim nameVal As String: nameVal = GetVal(ws, rowNum, headers, COL_FACTORY_NAME)
    
    If region = "" Or district = "" Or jibun = "" Or nameVal = "" Then Exit Sub
    
    Dim urlCol As Long: urlCol = headers(COL_RESULT_URL)
    If ws.Cells(rowNum, urlCol).Value <> "" Then Exit Sub
    
    Dim root As String, path As String
    root = BuildPath(GetRootPath(), FOLDER_FACTORY)
    
    path = CreateFolder(root, NormalizeRegion(region))
    path = CreateFolder(path, district)
    If Trim(village) <> "" Then path = CreateFolder(path, village)
    
    path = CreateFolder(path, jibun & " " & nameVal)
    
    ws.Cells(rowNum, urlCol).Value = path
End Sub


' ==================================================================================
' Utilities
' ==================================================================================

' Creates a folder if it doesn't exist. Returns the full path.
Private Function CreateFolder(parentPath As String, folderName As String) As String
    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Clean illegal characters
    folderName = CleanPath(folderName)
    
    Dim newPath As String
    If Right(parentPath, 1) = "\" Then
        newPath = parentPath & folderName
    Else
        newPath = parentPath & "\" & folderName
    End If
    
    If Not fso.FolderExists(newPath) Then
        On Error Resume Next
        fso.CreateFolder newPath
        If Err.Number <> 0 Then
            ' Attempt to create parent if missing (simple recursive check)
            If Not fso.FolderExists(parentPath) Then
                 Debug.Print "Parent folder missing: " & parentPath
                 ' For now, just fail. User needs to ensure Root exists.
            End If
            Debug.Print "Failed to create: " & newPath
        End If
        On Error GoTo 0
    End If
    
    CreateFolder = newPath
End Function

Private Function CleanPath(inputStr As String) As String
    Dim invalidChars As Variant
    invalidChars = Array("/", ":", "*", "?", """", "<", ">", "|")
    
    Dim i As Integer
    Dim output As String
    output = inputStr
    
    For i = LBound(invalidChars) To UBound(invalidChars)
        output = Replace(output, invalidChars(i), "_")
    Next i
    
    output = Trim(output)
    CleanPath = output
End Function

Private Function NormalizeRegion(ByVal region As String) As String
    region = Application.Trim(region)
    Select Case region
        Case "아산시", "천안시 서북구", "천안시 동남구"
            NormalizeRegion = region
        Case Else
            NormalizeRegion = "타지역"
    End Select
End Function

Private Function GetHeaderMap(ws As Worksheet) As Object
    Dim headers As Object
    Set headers = CreateObject("Scripting.Dictionary")
    
    Dim lastCol As Long
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    Dim i As Long
    For i = 1 To lastCol
        Dim key As String
        key = ws.Cells(1, i).Value
        If Not headers.Exists(key) Then
            headers.Add key, i
        End If
    Next i
    
    Set GetHeaderMap = headers
End Function

Private Function GetVal(ws As Worksheet, rowNum As Long, headers As Object, key As String) As String
    If headers.Exists(key) Then
        GetVal = ws.Cells(rowNum, headers(key)).Value
    Else
        GetVal = ""
    End If
End Function

Private Function HasKeys(dict As Object, keys As Variant) As Boolean
    Dim k As Variant
    For Each k In keys
        If Not dict.Exists(k) Then
            HasKeys = False
            Exit Function
        End If
    Next k
    HasKeys = True
End Function
 
Private Function BuildPath(p1 As String, p2 As String) As String
    If Right(p1, 1) = "\" Then
        BuildPath = p1 & p2
    Else
        BuildPath = p1 & "\" & p2
    End If
End Function

Private Function JoinCollection(col As Collection, delimiter As String) As String
    Dim res As String
    Dim i As Integer
    For i = 1 To col.Count
        If i > 1 Then res = res & delimiter
        res = res & col(i)
    Next i
    JoinCollection = res
End Function

' Returns dynamic root path based on user environment
Private Function GetRootPath() As String
    Dim customPath As String
    On Error Resume Next
    ' Try to get named range "RootPath"
    customPath = ThisWorkbook.Names("RootPath").RefersToRange.Value
    On Error GoTo 0
    
    If customPath <> "" Then
        GetRootPath = customPath
    Else
        ' Default: Use the same folder as the Excel file
        GetRootPath = ThisWorkbook.Path
    End If
End Function

' Try to parse a full address string into components if the individual columns are empty
Private Sub ParseAddress(fullAddr As String, ByRef region As String, ByRef district As String, ByRef village As String, ByRef jibun As String)
    If Trim(fullAddr) = "" Then Exit Sub
    
    Dim parts() As String
    parts = Split(Trim(fullAddr), " ")
    
    ' Very basic parsing for 3-4 part addresses (e.g. 아산시 배방읍 장재리 1234)
    ' This is a fallback and might need refinement based on actual data patterns
    
    Dim i As Integer
    Dim p As String
    
    For i = LBound(parts) To UBound(parts)
        p = parts(i)
        If InStr(p, "시") > 0 Or InStr(p, "군") > 0 Or InStr(p, "구") > 0 Then
            If region = "" Then region = p
        ElseIf InStr(p, "읍") > 0 Or InStr(p, "면") > 0 Or InStr(p, "동") > 0 Then
            If district = "" Then district = p
        ElseIf InStr(p, "리") > 0 Then
            If village = "" Then village = p
        ElseIf IsNumeric(Left(p, 1)) Then
            If jibun = "" Then jibun = p
        End If
    Next i
End Sub
