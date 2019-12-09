import { Component, OnInit } from '@angular/core';
import { UtilService } from '../../shared';

@Component({
  selector: 'app-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.scss']
})
export class UsersComponent implements OnInit {

  constructor(private utilService: UtilService) { }

  ngOnInit() {
  }

  public toggleSidebar(action: string) {
    this.utilService.toggleSidebar(action);
  }

}
