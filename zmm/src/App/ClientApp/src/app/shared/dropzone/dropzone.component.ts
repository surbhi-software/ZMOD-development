import { Component, OnInit, ViewChild, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { DropzoneComponent, DropzoneDirective, DropzoneConfigInterface } from 'ngx-dropzone-wrapper';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dropzone',
  templateUrl: './dropzone.component.html',
  styleUrls: ['./dropzone.component.scss']
})
export class AppDropzoneComponent implements OnInit, OnChanges {

  @ViewChild(DropzoneComponent) componentRef?: DropzoneComponent;
  @ViewChild(DropzoneDirective) directiveRef?: DropzoneDirective;
  @Input() dropzoneConfig: any = {};
  @Output() dropzoneSuccess = new EventEmitter<any>();
  @Input() openFileBrowserWindow: boolean;

  public config: DropzoneConfigInterface = {
    timeout: 0, // disabling timeout
    maxFilesize: 5000,
    clickable: true,
    maxFiles: 1000,
    autoReset: null,
    errorReset: null,
    cancelReset: null,
    // retryChunks: true,
    // chunking: true,      // enable chunking
    // forceChunking: true, // forces chunking when file.size < chunkSize
    // chunkSize: 1000000,  // chunk size 1,000,000 bytes (~1MB)
    // chunksUploaded: function (file, done) {
    //   console.log('chunksUploaded', file, done());
    //   done()
    // }
  };

  public toggleClickAction(): void {
    this.config.clickable = !this.config.clickable;
  }

  public resetDropzoneUploads(): void {
    this.componentRef.directiveRef.reset();
  }

  public openFileBrowser() {
    const element: HTMLElement = document.getElementsByClassName('dropzone')[0] as HTMLElement;
    element.click();
  }

  public onUploadError(args: any): void {
    console.log('onUploadError:', args);
  }

  public onUploadSuccess(args: any): void {
    console.log('onUploadSuccess:', args);
    this.dropzoneSuccess.emit(args);
  }

  constructor() { }

  ngOnChanges() {
    this.config.url = environment.serverUrl + this.dropzoneConfig.url;
    this.config.acceptedFiles = this.dropzoneConfig.acceptedFiles;
    if (this.openFileBrowserWindow) {
      this.openFileBrowser();
    }
  }

  ngOnInit() {
  }

}
