import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, fromEvent, merge, of } from 'rxjs';
import { mapTo } from 'rxjs/operators';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material';
import { DomSanitizer } from '@angular/platform-browser';
import { saveAs } from 'file-saver';
import { SnackbarComponent } from '../snackbar/snackbar.component';
import { environment } from '../../../environments/environment';
declare var require: any;

@Injectable({
  providedIn: 'root',
})
export class UtilService {

  sidebarBehavior = new BehaviorSubject('');
  sidebarAction = this.sidebarBehavior.asObservable();

  constructor(private snackBar: MatSnackBar, private sanitizer: DomSanitizer) { }

  getAppVersion() {
    return require('../../../../package.json').version;
  }

  toggleSidebar(action: string) {
    this.sidebarBehavior.next(action);
  }

  alert(message: string, action?: string, noAutoHide?: boolean) {
    const config: MatSnackBarConfig = {
      verticalPosition: 'bottom',
      horizontalPosition: 'left',
      duration: !noAutoHide ? 3000 : 0,
      data: { message: message, action: action }
    };
    return this.snackBar.openFromComponent(SnackbarComponent, config);
  }

  generateUniqueID() {
    return (Date.now().toString(36) + Math.random().toString(36).substr(2, 5)).toUpperCase();
  }

  transformUrl(url: string) {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  saveFile(response: any, filename: String) {
    saveAs(response, filename);
  }

  filterArray(arr: any[], key: string, value: any) {
    let obj = {
      index: -1,
      item: {}
    };
    if (arr && arr.length > 0) {
      arr.filter((item, index) => {
        if (item[key] === value) {
          return obj = {
            index: index,
            item: item
          };
        }
      });
    }
    return obj;
  }

  fileTypeIcon(type: string) {
    const iconSets = {
      FOLDER: 'mdi-folder',
      JSON: 'mdi-file',
      IMAGE: 'mdi-image',
      CSV: 'mdi-file-excel',
      PMML: 'mdi-file',
      PYTHON: 'mdi-file-code',
      JUPYTER_NOTEBOOK: 'mdi-file-document-outline',
      JNB: 'mdi-alpha-j-box',
      TB: 'mdi-alpha-t-box',
      ZMK: 'mdi-alpha-z-box',
      GPU: 'mdi-alpha-g-box',
      VIDEO: 'mdi-file-video'
    };
    if (iconSets[type]) {
      return iconSets[type];
    } else {
      return 'mdi-file';
    }
  }

  transformCSVDataToJson(res: String) {
    const allTextLines = res.split(/\r\n|\n/);
    const headers = allTextLines[0].split(',');
    const lines = [];
    for (let i = 1; i < allTextLines.length; i++) {
      const data = allTextLines[i].split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
      if (data.length === headers.length) {
        const tarr = {};
        for (let j = 0; j < headers.length; j++) {
          tarr[headers[j]] = data[j].replace(/["]/g, '');
        }
        lines.push(tarr);
      }
    }
    return { header: headers, data: lines };
  }

  checkInternetConnection(): Observable<boolean | {}> {
    return merge(of(navigator.onLine), fromEvent(window, 'online').pipe(mapTo(true)), fromEvent(window, 'offline').pipe(mapTo(false)));
  }

  getSettingsObject(type: string, settingsJSON: any) {
    if (settingsJSON) {
      const selectedArray = settingsJSON.settings.filter(function (element) {
        return (element.type === type && element.selected === true);
      });
      return selectedArray[0];
    } else {
      return undefined;
    }
  }

}
