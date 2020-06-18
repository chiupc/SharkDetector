from data_utils import *

def main():
    board=sys.argv[1]
    category=sys.argv[2]
    from_=sys.argv[3]
    to_=sys.argv[4]
    interval=sys.argv[5]
    mine_force_data(board,category,from_,to_,interval)
    bulk_update_threshold(category,interval)
    
if __name__ == "__main__":
    main()