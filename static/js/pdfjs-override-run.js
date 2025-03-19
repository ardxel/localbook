function overrideOptions() {
  if (!globalThis.PDFViewerApplication) {
    console.error("PDF.js is not loaded");
    return;
  }
  globalThis.PDFViewerApplicationOptions.set("workerSrc", window.PDF_WORKER);
  globalThis.PDFViewerApplicationOptions.set(
    "sandboxBundleSrc",
    window.PDF_SANDBOX,
  );

  globalThis.PDFViewerApplicationOptions.set("defaultUrl", window.PDF_FILE);
}

function getViewerConfiguration() {
  return {
    appContainer: document.body,
    principalContainer: document.getElementById("mainContainer"),
    mainContainer: document.getElementById("viewerContainer"),
    viewerContainer: document.getElementById("viewer"),
    toolbar: {
      container: document.getElementById("toolbarContainer"),
      numPages: document.getElementById("numPages"),
      pageNumber: document.getElementById("pageNumber"),
      scaleSelect: document.getElementById("scaleSelect"),
      customScaleOption: document.getElementById("customScaleOption"),
      previous: document.getElementById("previous"),
      next: document.getElementById("next"),
      zoomIn: document.getElementById("zoomInButton"),
      zoomOut: document.getElementById("zoomOutButton"),
      print: document.getElementById("printButton"),
      editorFreeTextButton: document.getElementById("editorFreeTextButton"),
      editorFreeTextParamsToolbar: document.getElementById(
        "editorFreeTextParamsToolbar",
      ),
      editorHighlightButton: document.getElementById("editorHighlightButton"),
      editorHighlightParamsToolbar: document.getElementById(
        "editorHighlightParamsToolbar",
      ),
      editorHighlightColorPicker: document.getElementById(
        "editorHighlightColorPicker",
      ),
      editorInkButton: document.getElementById("editorInkButton"),
      editorInkParamsToolbar: document.getElementById("editorInkParamsToolbar"),
      editorStampButton: document.getElementById("editorStampButton"),
      editorStampParamsToolbar: document.getElementById(
        "editorStampParamsToolbar",
      ),
      editorSignatureButton: document.getElementById("editorSignatureButton"),
      editorSignatureParamsToolbar: document.getElementById(
        "editorSignatureParamsToolbar",
      ),
      download: document.getElementById("downloadButton"),
    },
    secondaryToolbar: {
      toolbar: document.getElementById("secondaryToolbar"),
      toggleButton: document.getElementById("secondaryToolbarToggleButton"),
      presentationModeButton: document.getElementById("presentationMode"),
      openFileButton: document.getElementById("secondaryOpenFile"),
      printButton: document.getElementById("secondaryPrint"),
      downloadButton: document.getElementById("secondaryDownload"),
      viewBookmarkButton: document.getElementById("viewBookmark"),
      firstPageButton: document.getElementById("firstPage"),
      lastPageButton: document.getElementById("lastPage"),
      pageRotateCwButton: document.getElementById("pageRotateCw"),
      pageRotateCcwButton: document.getElementById("pageRotateCcw"),
      cursorSelectToolButton: document.getElementById("cursorSelectTool"),
      cursorHandToolButton: document.getElementById("cursorHandTool"),
      scrollPageButton: document.getElementById("scrollPage"),
      scrollVerticalButton: document.getElementById("scrollVertical"),
      scrollHorizontalButton: document.getElementById("scrollHorizontal"),
      scrollWrappedButton: document.getElementById("scrollWrapped"),
      spreadNoneButton: document.getElementById("spreadNone"),
      spreadOddButton: document.getElementById("spreadOdd"),
      spreadEvenButton: document.getElementById("spreadEven"),
      imageAltTextSettingsButton: document.getElementById(
        "imageAltTextSettings",
      ),
      imageAltTextSettingsSeparator: document.getElementById(
        "imageAltTextSettingsSeparator",
      ),
      documentPropertiesButton: document.getElementById("documentProperties"),
    },
    sidebar: {
      outerContainer: document.getElementById("outerContainer"),
      sidebarContainer: document.getElementById("sidebarContainer"),
      toggleButton: document.getElementById("sidebarToggleButton"),
      resizer: document.getElementById("sidebarResizer"),
      thumbnailButton: document.getElementById("viewThumbnail"),
      outlineButton: document.getElementById("viewOutline"),
      attachmentsButton: document.getElementById("viewAttachments"),
      layersButton: document.getElementById("viewLayers"),
      thumbnailView: document.getElementById("thumbnailView"),
      outlineView: document.getElementById("outlineView"),
      attachmentsView: document.getElementById("attachmentsView"),
      layersView: document.getElementById("layersView"),
      currentOutlineItemButton: document.getElementById("currentOutlineItem"),
    },
    findBar: {
      bar: document.getElementById("findbar"),
      toggleButton: document.getElementById("viewFindButton"),
      findField: document.getElementById("findInput"),
      highlightAllCheckbox: document.getElementById("findHighlightAll"),
      caseSensitiveCheckbox: document.getElementById("findMatchCase"),
      matchDiacriticsCheckbox: document.getElementById("findMatchDiacritics"),
      entireWordCheckbox: document.getElementById("findEntireWord"),
      findMsg: document.getElementById("findMsg"),
      findResultsCount: document.getElementById("findResultsCount"),
      findPreviousButton: document.getElementById("findPreviousButton"),
      findNextButton: document.getElementById("findNextButton"),
    },
    passwordOverlay: {
      dialog: document.getElementById("passwordDialog"),
      label: document.getElementById("passwordText"),
      input: document.getElementById("password"),
      submitButton: document.getElementById("passwordSubmit"),
      cancelButton: document.getElementById("passwordCancel"),
    },
    documentProperties: {
      dialog: document.getElementById("documentPropertiesDialog"),
      closeButton: document.getElementById("documentPropertiesClose"),
      fields: {
        fileName: document.getElementById("fileNameField"),
        fileSize: document.getElementById("fileSizeField"),
        title: document.getElementById("titleField"),
        author: document.getElementById("authorField"),
        subject: document.getElementById("subjectField"),
        keywords: document.getElementById("keywordsField"),
        creationDate: document.getElementById("creationDateField"),
        modificationDate: document.getElementById("modificationDateField"),
        creator: document.getElementById("creatorField"),
        producer: document.getElementById("producerField"),
        version: document.getElementById("versionField"),
        pageCount: document.getElementById("pageCountField"),
        pageSize: document.getElementById("pageSizeField"),
        linearized: document.getElementById("linearizedField"),
      },
    },
    altTextDialog: {
      dialog: document.getElementById("altTextDialog"),
      optionDescription: document.getElementById("descriptionButton"),
      optionDecorative: document.getElementById("decorativeButton"),
      textarea: document.getElementById("descriptionTextarea"),
      cancelButton: document.getElementById("altTextCancel"),
      saveButton: document.getElementById("altTextSave"),
    },
    newAltTextDialog: {
      dialog: document.getElementById("newAltTextDialog"),
      title: document.getElementById("newAltTextTitle"),
      descriptionContainer: document.getElementById(
        "newAltTextDescriptionContainer",
      ),
      textarea: document.getElementById("newAltTextDescriptionTextarea"),
      disclaimer: document.getElementById("newAltTextDisclaimer"),
      learnMore: document.getElementById("newAltTextLearnMore"),
      imagePreview: document.getElementById("newAltTextImagePreview"),
      createAutomatically: document.getElementById(
        "newAltTextCreateAutomatically",
      ),
      createAutomaticallyButton: document.getElementById(
        "newAltTextCreateAutomaticallyButton",
      ),
      downloadModel: document.getElementById("newAltTextDownloadModel"),
      downloadModelDescription: document.getElementById(
        "newAltTextDownloadModelDescription",
      ),
      error: document.getElementById("newAltTextError"),
      errorCloseButton: document.getElementById("newAltTextCloseButton"),
      cancelButton: document.getElementById("newAltTextCancel"),
      notNowButton: document.getElementById("newAltTextNotNow"),
      saveButton: document.getElementById("newAltTextSave"),
    },
    altTextSettingsDialog: {
      dialog: document.getElementById("altTextSettingsDialog"),
      createModelButton: document.getElementById("createModelButton"),
      aiModelSettings: document.getElementById("aiModelSettings"),
      learnMore: document.getElementById("altTextSettingsLearnMore"),
      deleteModelButton: document.getElementById("deleteModelButton"),
      downloadModelButton: document.getElementById("downloadModelButton"),
      showAltTextDialogButton: document.getElementById(
        "showAltTextDialogButton",
      ),
      altTextSettingsCloseButton: document.getElementById(
        "altTextSettingsCloseButton",
      ),
      closeButton: document.getElementById("altTextSettingsCloseButton"),
    },
    addSignatureDialog: {
      dialog: document.getElementById("addSignatureDialog"),
      panels: document.getElementById("addSignatureActionContainer"),
      typeButton: document.getElementById("addSignatureTypeButton"),
      typeInput: document.getElementById("addSignatureTypeInput"),
      drawButton: document.getElementById("addSignatureDrawButton"),
      drawSVG: document.getElementById("addSignatureDraw"),
      drawPlaceholder: document.getElementById("addSignatureDrawPlaceholder"),
      drawThickness: document.getElementById("addSignatureDrawThickness"),
      imageButton: document.getElementById("addSignatureImageButton"),
      imageSVG: document.getElementById("addSignatureImage"),
      imagePlaceholder: document.getElementById("addSignatureImagePlaceholder"),
      imagePicker: document.getElementById("addSignatureFilePicker"),
      imagePickerLink: document.getElementById("addSignatureImageBrowse"),
      description: document.getElementById("addSignatureDescription"),
      clearButton: document.getElementById("clearSignatureButton"),
      saveContainer: document.getElementById("addSignatureSaveContainer"),
      saveCheckbox: document.getElementById("addSignatureSaveCheckbox"),
      errorBar: document.getElementById("addSignatureError"),
      errorCloseButton: document.getElementById("addSignatureErrorCloseButton"),
      cancelButton: document.getElementById("addSignatureCancelButton"),
      addButton: document.getElementById("addSignatureAddButton"),
    },
    editSignatureDialog: {
      dialog: document.getElementById("editSignatureDescriptionDialog"),
      description: document.getElementById("editSignatureDescription"),
      editSignatureView: document.getElementById("editSignatureView"),
      cancelButton: document.getElementById("editSignatureCancelButton"),
      updateButton: document.getElementById("editSignatureUpdateButton"),
    },
    annotationEditorParams: {
      editorFreeTextFontSize: document.getElementById("editorFreeTextFontSize"),
      editorFreeTextColor: document.getElementById("editorFreeTextColor"),
      editorInkColor: document.getElementById("editorInkColor"),
      editorInkThickness: document.getElementById("editorInkThickness"),
      editorInkOpacity: document.getElementById("editorInkOpacity"),
      editorStampAddImage: document.getElementById("editorStampAddImage"),
      editorSignatureAddSignature: document.getElementById(
        "editorSignatureAddSignature",
      ),
      editorFreeHighlightThickness: document.getElementById(
        "editorFreeHighlightThickness",
      ),
      editorHighlightShowAll: document.getElementById("editorHighlightShowAll"),
    },
    printContainer: document.getElementById("printContainer"),
    editorUndoBar: {
      container: document.getElementById("editorUndoBar"),
      message: document.getElementById("editorUndoBarMessage"),
      undoButton: document.getElementById("editorUndoBarUndoButton"),
      closeButton: document.getElementById("editorUndoBarCloseButton"),
    },
  };
}
function webViewerLoad() {
  overrideOptions();
  const config = getViewerConfiguration();
  const event = new CustomEvent("webviewerloaded", {
    bubbles: true,
    cancelable: true,
    detail: {
      source: window,
    },
  });
  try {
    parent.document.dispatchEvent(event);
  } catch (ex) {
    console.error("webviewerloaded:", ex);
    document.dispatchEvent(event);
  }
  window.PDFViewerApplication.run(config);
}
document.blockUnblockOnload?.(true);
if (
  document.readyState === "interactive" ||
  document.readyState === "complete"
) {
  webViewerLoad();
} else {
  document.addEventListener("DOMContentLoaded", webViewerLoad, true);
}
